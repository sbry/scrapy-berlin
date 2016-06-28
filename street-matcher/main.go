package main

import (
	"encoding/json"
	"fmt"
	"html"
	"io/ioutil"
	"log"
	"os"
	"regexp"
	"strings"
)

// a range of maps of strings to interface{}
// and it must be that because there are strings and integers
func get_streets() []map[string]interface{} {
	json_string, err := ioutil.ReadFile("./streets.json")
	if err != nil {
		log.Fatal(err)
	}
	// need to give the json-parser a hint what we have got
	var data []map[string]interface{}
	err = json.Unmarshal(json_string, &data)
	if err != nil {
		log.Fatal(err)
	}
	return data
}

func get_article(filename string) string {
	file_bytes, err := ioutil.ReadFile(filename)
	if err != nil {
		log.Fatal(err)
	}
	// lots of cleaning for real hits
	file_string := strings.ToLower(html.UnescapeString(string(file_bytes)))
	re := regexp.MustCompile(" +")
	return re.ReplaceAllLiteralString(file_string, " ")
}

func main() {
	streets := get_streets()
	for _, filename := range os.Args[1:] {
		article_string := get_article(string(filename))
		for _, v := range streets {
			street_name := strings.ToLower(v["title"].(string))
			is_hit := strings.Contains(article_string, street_name)
			if is_hit {
				fmt.Println(street_name, v["district"], is_hit)
			}
		}
	}
}
