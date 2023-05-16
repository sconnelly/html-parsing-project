from html.parser import HTMLParser

def hasColor(attrs):
    if len(attrs) == 0 or attrs[0][0] != "style":
        return False
    style = attrs[0][1]
    if style == "color: rgb(0,0,255);" or style == "color: rgb(255,153,0);":
        return True
    return False

class TermParser(HTMLParser):
    branch = [] 
    state = 0 
    terms = []
    def handle_starttag(x, tag, attrs):
        if len(x.branch) == 0:
            # looking for container div - this is a stressful mess because the lack of consistency is worse than I anticipated! 
            if tag == "div" and len(attrs) > 0 and attrs[0][0] == "id" and attrs[0][1] == "main-content":
                x.branch.append(tag)
                x.state = 1
        else:
            x.branch.append(tag)
            
            if x.state == 1 and x.branch == ["div", "p", "span"] and hasColor(attrs):
                x.state = 2
            elif x.state == 2 and tag == "strong":
                x.state = 3
            elif x.state == 3:
                x.state = 1
            elif x.state == 4 and len(x.branch) == 2:
                if tag == "ul":
                    x.state = 5
                else:
                    x.state = 1

    def handle_data(x, data):
        if x.state == 3:
            x.terms.append({"Term": data})
            x.state = 4
        elif x.state == 5:
            print(data)
            
            i = data.index(":")
            typ = data[:i]
            info = data[i+2:]

            n = len(x.terms) - 1
            if typ in x.terms[n]:
                x.terms[n][typ] += "\n" + info
            
            else:
                x.terms[n][typ] = info

    def handle_endtag(x, tag):
        n = len(x.branch)
        if n > 0:
            i = n - 1
            while i >= 0:
                tip = x.branch[i]
                x.branch.pop()
                if tip == tag:
                    break
                i -= 1
            else:
                print("invalid HTML")

            if len(x.branch) == 0:
                x.state = 0
            elif x.state == 2 and x.branch == ["div", "p"]:
                x.state = 1
            elif x.state == 5 and len(x.branch) == 1:
                x.state = 1

parser = TermParser()

f = open("terminology.html", "r", encoding="utf-8")
parser.feed(f.read())
f.close()

f = open("terminology.csv", "w", encoding="utf-8", newline="")

fieldnames = ["Term", "Definition", "Example(s)", "Usage"]
w = csv.DictWriter(f, fieldnames=fieldnames)

w.writeheader()
for term in parser.terms:
    w.writerow(term)

f.close()
