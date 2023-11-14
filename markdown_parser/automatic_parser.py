import os

PWD = "astro-rewrite/src/content/docs/"

class html_object:
    def __init__(self, path, output_path, title):
        self.path = path
        self.output_path = output_path
        self.title = title
input_output = [
    html_object("overview.html", PWD + "overview/overview.md", "Autonome Systeme - Um was geht's hier"),

    html_object("semWi23-24.html", PWD + "semesterplan/semWi23-24.md", "Autonome Systeme - Winter Semester 23/24"),

    html_object("lec-concurrency-go.html", PWD + "teil_1/lec-concurrency-go.md", "Die Programmiersprache Go"),
    html_object("lec-concurrency-models.html", PWD + "teil_1/lec-concurrency-models.md", "Concurrency models"),
    html_object("lec-futures.html", PWD + "teil_1/lec-futures.md", "Futures and Promises"),

    html_object("lec-modelling-specification.html", PWD + "teil_2/lec-modelling-specification.md", "Model-Based Specification"),
    html_object("lec-resource-usage.html", PWD + "teil_2/lec-resource-usage.md", "Resource usage (dynamic and static) verification"),
    html_object("lec-data-race.html", PWD + "teil_2/lec-data-race.md", "Dynamic data race prediction"),
    html_object("lec-hb-vc.html", PWD + "teil_2/lec-hb-vc.md", "Dynamic data race prediction - Happens-before and vector clocks"),
    html_object("lec-deadlock.html", PWD + "teil_2/lec-deadlock.md", "Dynamic deadlock prediction"),
    html_object("verification-notes.html", PWD + "teil_2/verification-notes.md", "Dynamic verification - data races and deadlocks"),

    html_object("uppaal.html", PWD + "uppaal/uppaal.md", "UPPAAL Labor"),
]



for obj in input_output:
    os.system("cat " + obj.path + " | pandoc --from html --to markdown_strict -o " + obj.output_path)
    with open(obj.output_path, "r") as f:
        content = f.read()
        doc_start = f"---\ntitle: {obj.title}\ndescription: Martin Sulzmann\n---"

        # replace duplicate description
        content = content.replace("Martin Sulzmann", "")

        content = doc_start + content

        # replace dublicate title
        content = content.replace("# " + obj.title, "")

    with open(obj.output_path, "w") as f:
        f.write(content)
