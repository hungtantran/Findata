package main

import (
    "bytes"
    "encoding/json"
    "errors"
    "fmt"
    "sync"
    "io/ioutil"
    "log"
    "net/http"
    "time"
    //"github.com/davecgh/go-spew/spew"
    "golang.org/x/net/html"

    "fin_database"
    "utilities"
)

type WSJDocObject struct {
	Link string
    Headline string
    Abstract string
}

var WSJ_API string = "http://www.wsj.com/public/page/archive-%d-%d-%d.html";

type WSJCrawler struct {
    waitGroup *sync.WaitGroup
    newsInfoDatabase *fin_database.NewsInfoDatabase
    newsContentDatabase *fin_database.NewsContentDatabase
    startDayFromToday int
    endDayFromToday int
    updateFrequencySecs int
    waitSecsBeforeRestart int
}

func NewWSJCrawler(
        waitGroup *sync.WaitGroup,
        newsInfoDatabase *fin_database.NewsInfoDatabase,
        newsContentDatabase *fin_database.NewsContentDatabase,
        startDayFromToday int,
        endDayFromToday int,
        updateFrequencySecs int,
        waitSecsBeforeRestart int) *WSJCrawler {
    var wsjCrawler *WSJCrawler = new(WSJCrawler);
    wsjCrawler.waitGroup = waitGroup;
    wsjCrawler.newsInfoDatabase = newsInfoDatabase;
    wsjCrawler.newsContentDatabase = newsContentDatabase;
    wsjCrawler.startDayFromToday = startDayFromToday;
    wsjCrawler.endDayFromToday = endDayFromToday;
    wsjCrawler.updateFrequencySecs = updateFrequencySecs;
    wsjCrawler.waitSecsBeforeRestart = waitSecsBeforeRestart;
    return wsjCrawler;
}

func (wsjCrawler *WSJCrawler) Crawl() {
    for {
        err := wsjCrawler.CrawlOneTry();
        if (err != nil) {
            log.Println(err);
            wsjCrawler.waitGroup.Done();
            return;
        }
        time.Sleep(time.Duration(wsjCrawler.updateFrequencySecs) * time.Second);
    }
}

func (wsjCrawler *WSJCrawler) CrawlOneTry() error {
    numErr := 0;
    
    curDayFromToday := wsjCrawler.startDayFromToday;
    for {
        if (curDayFromToday > wsjCrawler.endDayFromToday) {
            break;
        }
        curDate := time.Now().AddDate(0, 0, -curDayFromToday);
        year := curDate.Year();
        month := curDate.Month();
        day := curDate.Day();
        var curLink string = fmt.Sprintf(WSJ_API, year, month, day);
        log.Printf("Processing page with link %s", curLink);
        resp, err := http.Get(curLink);
        if (err != nil) {
            numErr++;
            if (numErr > MAX_ERR) {
                return errors.New("Exceed max num error");
            }
            continue;
        }
        defer resp.Body.Close();
        body, err := ioutil.ReadAll(resp.Body);
        var docObjects []WSJDocObject = wsjCrawler.ParseOnePage(string(body));
        for _, doc := range docObjects {
            newsInfo := wsjCrawler.ConvertDocObjectToNewsInfo(doc, curDate);
            insertId := wsjCrawler.newsInfoDatabase.InsertNewsInfo(&newsInfo);

            newsContent := wsjCrawler.ConvertDocObjectToNewsContent(doc);
            newsContent.Id.Int64 = insertId;
            newsContent.Id.Valid = true;
            wsjCrawler.newsContentDatabase.InsertNewsContent(&newsContent);

            log.Printf("Insert news (%d) (%s) with headline %s", insertId, newsInfo.Link, newsInfo.Headline);
        }
        time.Sleep(time.Duration(wsjCrawler.waitSecsBeforeRestart) * time.Second);
        curDayFromToday++;
    }
    return nil;
}

func (wsjCrawler *WSJCrawler) ConvertDocObjectToNewsContent(doc WSJDocObject) fin_database.NewsContent {
    var newsContent fin_database.NewsContent;
    docJson, _ := json.Marshal(doc);
    newsContent.FullData.String = string(docJson);  
    newsContent.FullData.Valid = true;
    return newsContent;
}

func (wsjCrawler *WSJCrawler) ConvertDocObjectToNewsInfo(doc WSJDocObject, date time.Time) fin_database.NewsInfo {
    Source := "wsj";
    Headline := doc.Headline;
    Abstract := doc.Abstract;
    Link := doc.Link;

    var newsInfo fin_database.NewsInfo;
    newsInfo.Source.String = Source;
    newsInfo.Source.Valid = true;
    newsInfo.Date = date;
    newsInfo.Headline.String = Headline;
    newsInfo.Headline.Valid = true;
    newsInfo.Abstract.String = Abstract;
    newsInfo.Abstract.Valid = true;
    newsInfo.Link.String = Link;
    newsInfo.Link.Valid = true;
    return newsInfo;
}

func (wsjCrawler *WSJCrawler) ParseOnePage(content string) []WSJDocObject {
    var docs []WSJDocObject;
    reader := bytes.NewBufferString(content)
    doc, err := html.Parse(reader)
    if err != nil {
        log.Println("Can't parse wsj html");
        return docs;
    }

    var newsItemNodes []*html.Node;
    attrKeys := []string{"class"};
    attrValues := []string{"newsItem"};
    utilities.ExtractItemsFromNode(
        doc, "ul", attrKeys, attrValues, &newsItemNodes);
    if (len(newsItemNodes) != 1) {
        log.Printf("Find %d news item node", len(newsItemNodes));
        return docs;
    }

    var extractDocOjects func(newsNode *html.Node);
    // Each newsNode is like
    // <li>
    //     <h2><a href="http://www.wsj.com/articles/oregon-standoff-leader-ammon-bundy-testifies-in-trial-1475725752">Oregon Standoff Leader Ammon Bundy Testifies in Trial</a></h2>
    //     <p>
    //             Oregon Standoff Leader Ammon Bundy Testifies in Trial 
    //     The leader of a 41-day standoff at a national wildlife refuge in Oregon testified Wednesday that he orchestrated the takeover to take “a hard stand” against the federal government’s control of public lands and said the occupiers would not be successful unless they carried guns.</p>
    // </li>
    extractDocOjects = func(newsNode *html.Node) {
        for newsNode := newsNode.FirstChild; newsNode != nil; newsNode = newsNode.NextSibling {
            if (newsNode.Type == html.ElementNode && newsNode.Data == "li") {
                var headlineNode *html.Node = nil;
                var abstractNode *html.Node = nil;
                for child := newsNode.FirstChild; child != nil; child = child.NextSibling {
                    if (child.Type == html.ElementNode && child.Data == "h2") {
                        headlineNode = child;
                    }
                    if (child.Type == html.ElementNode && child.Data == "p") {
                        abstractNode = child;
                    }
                }

                if (headlineNode == nil || abstractNode == nil) {
                    continue;
                }

                var wsjDocObject WSJDocObject;
                for child := headlineNode.FirstChild; child != nil; child = child.NextSibling {
                    if (child.Type == html.ElementNode && child.Data == "a" &&
                        len(child.Attr) == 1 && child.Attr[0].Key == "href") {
                        wsjDocObject.Link = child.Attr[0].Val;
                        for grandChild := child.FirstChild; grandChild != nil; grandChild = grandChild.NextSibling {
                            if (grandChild.Type == html.TextNode) {
                                wsjDocObject.Headline = grandChild.Data;
                            }
                        }
                    }
                }

                for child := abstractNode.FirstChild; child != nil; child = child.NextSibling {
                    if (child.Type == html.TextNode) {
                        wsjDocObject.Abstract = child.Data;
                    }
                }

                if (wsjDocObject.Link == "" || wsjDocObject.Headline == "" || wsjDocObject.Abstract == "") {
                    continue;
                }
                docs = append(docs, wsjDocObject);
            }
        }
    }
    extractDocOjects(newsItemNodes[0]);
    return docs;
}