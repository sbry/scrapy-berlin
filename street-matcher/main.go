package main

// building for ARM
// GOOS=linux GOARCH=arm go build main.go
// batch-call (only one in parallel on the weak ARM)
// find $archiveDir -type f -print0 | xargs -0 -P1 -n1000 ./main

import (
	"encoding/json"
	"fmt"
	"html"
	"io/ioutil"
	"os"
	"path/filepath"
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

func parse_filename(absolute_filename string) ([]string, string, string) {
	basename := filepath.Base(absolute_filename)
	dir_parts := strings.Split(filepath.Dir(absolute_filename), "/")
	extension := filepath.Ext(basename)
	naked_filename := strings.TrimSuffix(basename, extension)
	return dir_parts, naked_filename, extension
}

func build_filename(dir_parts []string, naked_filename string, extension string) string {
	return filepath.Join(strings.Join(dir_parts, "/"), naked_filename+extension)
}

// a range of maps of strings to []byte
// and it must be that because there are strings and integers
func read_streets() []Street {
	var streets []Street
	err := json.Unmarshal(read_file("streets.json"), &streets)
	check(err)
	return streets
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func read_file(filename string) []byte {
	file_bytes, err := ioutil.ReadFile(filename)
	check(err)
	return file_bytes
}

func write_file(filename string, content []byte) {
	dirname := filepath.Dir(filename)
	if _, err := os.Stat(dirname); os.IsNotExist(err) {
		os.MkdirAll(dirname, 0777)
	}
	err := ioutil.WriteFile(filename, content, 0644)
	check(err)
}

func normalize_for_matching(s string) string {
	re := regexp.MustCompile(" +")
	return strings.ToLower(html.UnescapeString(re.ReplaceAllLiteralString(s, " ")))
}

func put_matched_streets(filename string, matched_streets []Street) {
	dir_parts, naked_filename, _ := parse_filename(filename)
	dir_parts[len(dir_parts)-1] = "streets"
	target_filename := build_filename(dir_parts, naked_filename, ".json")
	content, err := json.Marshal(matched_streets)
	check(err)
	write_file(target_filename, content)
}

func main() {
	streets := read_streets()
	for _, filename := range os.Args[1:] {
		var matched_streets []Street
		article_string := normalize_for_matching(string(read_file(string(filename))))
		for _, street := range streets {
			matched := strings.Contains(article_string, normalize_for_matching(street.Name))
			if matched {
				matched_streets = append(matched_streets, street)
			}
		}
		fmt.Println(matched_streets)
		put_matched_streets(filename, matched_streets)
	}
	fmt.Println("")
}
