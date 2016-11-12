package utilities

import (
    "golang.org/x/net/html"
)

func ExtractItemsFromNode(n *html.Node,
                          data string,
                          firstAttrKey string,
                          firstAttrVal string, 
                          items []*html.Node) {
    attributes := n.Attr;
    if (n.Type == html.ElementNode &&
        n.Data == data &&
        len(attributes) > 0 &&
        attributes[0].Key == firstAttrKey &&
        attributes[0].Val == firstAttrVal)  {
        item := n;
        items = append(items, item);
    }
    for c := n.FirstChild; c != nil; c = c.NextSibling {
        ExtractItemsFromNode(c, data, firstAttrKey, firstAttrVal, items);
    }
}