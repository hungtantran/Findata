package main

import (
    "encoding/json"
    "errors"
    "fmt"
    "io/ioutil"
    "log"
    "net/http"
    "time"

    "fin_database"
    //"github.com/davecgh/go-spew/spew"
)

type NytimesJsonObject struct {
	Response ResponseObject
	Status string
	Copyright string
}

type ResponseObject struct {
	Meta MetaObject
	Docs []DocObject
}

type MetaObject struct {
	Hits int
	Time int
	Offset int
}

type DocObject struct {
	Snippet string
	Abstract string
	Lead_Paragraph string
	Headline HeadLineObject
	Type_Of_Material string
	News_Desk string
	Section_Name SectionNameObject
	Subsection_Name SubSectionNameObject
	Pub_Date string
	Created string
	Updated string
	Source string
	Print_Section string
	Print_Page string
	Nytddes []string
	Web_Url string
	Taxonomy_Nodes string
	Keywords []KeywordObject
	Byline string
	Pay string
	Multimedia []MultimediaObject
	Document_Type string
	Asset_Id string
	Id string `json:"_id"`
	Timesmachine_Url string
}

type HeadLineObject struct {
	Main string
	Print_Headline string
}

type SectionNameObject struct {
	Content string
	Url string
	Display_Name string
}

type SubSectionNameObject struct {
	Content string
	Url string
	Display_Name string	
}

type KeywordObject struct {
	Rank string
	Is_Major string
	Name string
	Value string
}

type MultimediaObject struct {
	Width int
	Url string
	Height int
	Subtype string
	Legacy string
	Type string
}

var NYTIMES_API string = "http://query.nytimes.com/svc/add/v1/sitesearch.json?end_date=%04d%02d%02d&begin_date=%04d%02d%02d&page=%d";
var MAX_ERR int = 3;

type NYTimesCrawler struct {
    newsInfoDatabase *fin_database.NewsInfoDatabase
    newsContentDatabase *fin_database.NewsContentDatabase
    startDayFromToday int
    endDayFromToday int
    maxPageDepthPerDay int
    updateFrequencySecs int
    waitSecsBeforeRestart int
}

func NewNYTimesCrawler(
        newsInfoDatabase *fin_database.NewsInfoDatabase,
        newsContentDatabase *fin_database.NewsContentDatabase,
        startDayFromToday int,
        endDayFromToday int,
        maxPageDepthPerDay int,
        updateFrequencySecs int,
        waitSecsBeforeRestart int) *NYTimesCrawler {
    var nytimesCrawler *NYTimesCrawler = new(NYTimesCrawler);
    nytimesCrawler.newsInfoDatabase = newsInfoDatabase;
    nytimesCrawler.newsContentDatabase = newsContentDatabase;
    nytimesCrawler.startDayFromToday = startDayFromToday;
    nytimesCrawler.endDayFromToday = endDayFromToday;
    nytimesCrawler.maxPageDepthPerDay = maxPageDepthPerDay;
    nytimesCrawler.updateFrequencySecs = updateFrequencySecs;
    nytimesCrawler.waitSecsBeforeRestart = waitSecsBeforeRestart;
    return nytimesCrawler;
}

func (nytimesCrawler *NYTimesCrawler) Crawl() {
    for {
        err := nytimesCrawler.CrawlOneTry();
        if (err != nil) {
            log.Println(err);
            return;
        }
        time.Sleep(time.Duration(nytimesCrawler.updateFrequencySecs) * time.Second);
    }
}

func (nytimesCrawler *NYTimesCrawler) CrawlOneTry() error {
    numErr := 0;
    
    curDayFromToday := nytimesCrawler.startDayFromToday;
    for {
        if (curDayFromToday > nytimesCrawler.endDayFromToday) {
            break;
        }
        curDate := time.Now().AddDate(0, 0, -curDayFromToday);
        for curPage := 0; curPage < nytimesCrawler.maxPageDepthPerDay; curPage++ {
            if (curPage > nytimesCrawler.maxPageDepthPerDay) {
                break;
            }
            
            year := curDate.Year();
            month := curDate.Month();
            day := curDate.Day();
            var curLink string = fmt.Sprintf(NYTIMES_API, year, month, day, year, month, day, curPage);
            log.Printf("Processing page %d with link %s", curPage, curLink);
            resp, err := http.Get(curLink);
            if (err != nil) {
                numErr++;
                if (numErr > MAX_ERR) {
                    return errors.New("Exceed max num error");
                }
                continue;
            }
            defer resp.Body.Close()
            body, err := ioutil.ReadAll(resp.Body)
            var jsonObject NytimesJsonObject = nytimesCrawler.ParseOnePage(body);
            for _, doc := range jsonObject.Response.Docs {
                newsInfo := nytimesCrawler.ConvertDocObjectToNewsInfo(doc);
                insertId := nytimesCrawler.newsInfoDatabase.InsertNewsInfo(&newsInfo);
                //var insertId int64 = 0;

                newsContent := nytimesCrawler.ConvertDocObjectToNewsContent(doc);
                newsContent.Id.Int64 = insertId;
                newsContent.Id.Valid = true;
                nytimesCrawler.newsContentDatabase.InsertNewsContent(&newsContent);

                log.Printf("Insert news (%d) (%s) with headline %s", insertId, newsInfo.Link, newsInfo.Headline);
                //spew.Dump(newsInfo);
                //spew.Dump(newsContent);
            }
            time.Sleep(time.Duration(nytimesCrawler.waitSecsBeforeRestart) * time.Second);
        }
        curDayFromToday++;
    }
    return nil;
}

func (nytimesCrawler *NYTimesCrawler) ConvertDocObjectToNewsContent(doc DocObject) fin_database.NewsContent {
    var newsContent fin_database.NewsContent;
    docJson, _ := json.Marshal(doc);
    newsContent.FullData.String = string(docJson);  
    newsContent.FullData.Valid = true;
    return newsContent;
}

func (nytimesCrawler *NYTimesCrawler) ConvertDocObjectToNewsInfo(doc DocObject) fin_database.NewsInfo {
    Source := "nytimes";
    Date, err := time.Parse(time.RFC3339, doc.Pub_Date);
    if err != nil {
        log.Println("Can't parse pub date " + doc.Pub_Date);
    }
    Headline := doc.Headline.Main;
    PrintHeadline := doc.Headline.Print_Headline;
    Abstract := doc.Abstract;
    Section := doc.Section_Name.Content;
    Subsection := doc.Subsection_Name.Content;

    Tags := "";
    for _, tag := range doc.Nytddes {
        Tags += tag + ";";
    }

    Keywords := "";
    for _, keyword := range doc.Keywords {
        Keywords += keyword.Name + ":" + keyword.Value + ";";
    }

    Link := doc.Web_Url;
    Authors := doc.Byline;

    var newsInfo fin_database.NewsInfo;
    newsInfo.Source.String = Source;
    newsInfo.Source.Valid = true;
    newsInfo.Date = Date;
    newsInfo.Headline.String = Headline;
    newsInfo.Headline.Valid = true;
    newsInfo.PrintHeadline.String = PrintHeadline;
    newsInfo.PrintHeadline.Valid = true;
    newsInfo.Abstract.String = Abstract;
    newsInfo.Abstract.Valid = true;
    newsInfo.Section.String = Section;
    newsInfo.Section.Valid = true;
    newsInfo.Subsection.String = Subsection;
    newsInfo.Subsection.Valid = true;
    newsInfo.Tags.String = Tags;
    newsInfo.Tags.Valid = true;
    newsInfo.Keywords.String = Keywords;
    newsInfo.Keywords.Valid = true;
    newsInfo.Link.String = Link;
    newsInfo.Link.Valid = true;
    newsInfo.Authors.String = Authors;
    newsInfo.Authors.Valid = true;
    return newsInfo;
}

func (nytimesCrawler *NYTimesCrawler) ParseOnePage(contentJson []byte) NytimesJsonObject {
    var jsonObject NytimesJsonObject;
    json.Unmarshal(contentJson, &jsonObject);
    //spew.Dump(newsInfos);
    return jsonObject;
}