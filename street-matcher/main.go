package main

// building for ARM
// GOOS=linux GOARCH=arm go build main.go
// batch-call (only one in parallel on the weak ARM)
// find $archiveDir -type f -print0 | xargs -0 -P1 -n1000 ./main

import (
	"encoding/json"
	"fmt"
	"github.com/sbry/helper"
	"html"
	"io/ioutil"
	"os"
	"regexp"
	"strings"
)

// item of the json-file
type Street struct {
	District string `json:"district"`
	Name     string `json:"title"`
	// strange stuff data is mixed float and string,
	// f, err := strconv.ParseFloat("3.1415", 64)
	Lat interface{} `json:"lat"`
	Lng interface{} `json:"lng"`
}

// a range of maps of strings to []byte
// and it must be that because there are strings and integers
func read_streets() []Street {
	var streets []Street
	file_bytes, err := ioutil.ReadFile("streets.json")
	check(err)
	err = json.Unmarshal(file_bytes, &streets)
	check(err)
	return streets
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func normalize_for_matching(s string) string {
	re := regexp.MustCompile(" +")
	return strings.ToLower(html.UnescapeString(re.ReplaceAllLiteralString(s, " ")))
}

func main() {
	streets := read_streets()
	for _, filename := range os.Args[1:] {
		var matched_streets []Street
		helperFile := helper.NewFromPath(filename)
		article_string := normalize_for_matching(string(helperFile.Read()))
		for _, street := range streets {
			matched := strings.Contains(article_string, normalize_for_matching(street.Name))
			if matched {
				matched_streets = append(matched_streets, street)
			}
		}
		fmt.Println(matched_streets)
		// prepare output
		content, err := json.Marshal(matched_streets)
		check(err)
		// and write to new "collection"
		helperFile.SetCollection("streets")
		helperFile.SetExtension(".json")
		helperFile.Write(content)
	}
	fmt.Println("")
}
