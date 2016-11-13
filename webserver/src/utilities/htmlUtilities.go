package utilities

import (
    "golang.org/x/net/html"
)

func ExtractItemsFromNode(n *html.Node,
                          data string,
                          attrKeys []string,
                          attrVals []string, 
                          items *[]*html.Node) {
    if (len(attrKeys) != len(attrVals)) {
        return;
    }

    attributes := n.Attr;
    if (n.Type == html.ElementNode &&
        n.Data == data)  {
        if (len(attributes) >= len(attrKeys)) {
            match := true;
            for index, _ := range(attrKeys) {
                if (attributes[index].Key != attrKeys[index] ||
                    attributes[index].Val != attrVals[index]) {
                    match = false;
                    break;
                }
            }
            if (match) {
                item := n;
                *items = append(*items, item);
            }
        }
    }
    for c := n.FirstChild; c != nil; c = c.NextSibling {
        ExtractItemsFromNode(c, data, attrKeys, attrVals, items);
    }
}

func ExtractFirstTextFromNode(n *html.Node) string {
    result := "";
    for child := n.FirstChild; child != nil; child = child.NextSibling {
        if (child.Type == html.TextNode) {
            result = child.Data;
            break;
        } else if (child.Type == html.ElementNode) {
            result = ExtractFirstTextFromNode(child);
            if (result != "") {
                break;
            }
        }
    }
    return result;
}