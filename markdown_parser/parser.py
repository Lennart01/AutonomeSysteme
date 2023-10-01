from bs4 import BeautifulSoup
import markdownify
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='input file path', required=True)
parser.add_argument('-o', '--output', help='output file path', required=True)
args = parser.parse_args()

INPUT_FILE = args.input
OUTPUT_FILE = args.output

with open(INPUT_FILE, 'r') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# find all divs with class slide section level1
slides = soup.find_all('div', {'class': 'slide section level1'})

# find the index of the first slide
first_slide_index = 0
for i, slide in enumerate(slides):
    if 'slide-title' in slide['class']:
        first_slide_index = i
        break

# discard everything before the first slide
slides = slides[first_slide_index:]

markdown_lines = []

for slide in slides:
    lines = str(slide).split('\n')
    for line in lines:
        if '<h1>' in line:
            markdown_lines.append('## ' + line.replace('<h1>', '').replace('</h1>', ''))
            lines.remove(line)
        elif '<h2>' in line or '<h3>' in line or '<h4>' in line:
            markdown_lines.append('### ' + line.replace('<h2>', '').replace('</h2>', '').replace('<h3>', '').replace('</h3>', '').replace('<h4>', '').replace('</h4>', ''))
            lines.remove(line)
    
    text_lines = '\n'.join(lines)

    markdown_lines.append(markdownify.markdownify(text_lines))

code_block_ended = True
md_lines =  '\n'.join(markdown_lines).split('\n')
md_lines_edit = []
for md_line in md_lines:
    if '```' in md_line and code_block_ended:
        md_line = md_line.replace('```', '```go')
        md_lines_edit.append(md_line)
        code_block_ended = False
        continue
    if '```' in md_line and not code_block_ended:
        code_block_ended = True
        md_lines_edit.append(md_line)
    else:
        md_lines_edit.append(md_line)

with open(OUTPUT_FILE, 'w') as f:
    f.write('\n'.join(md_lines_edit))
