import csv
from html.parser import HTMLParser

# Working version, roughly equivalent to the final version of code writen for the Visier project.
# Nice to have (next iteration): search criteria outside of code for easier edits
# Version 2
# General observations:
# All the elements we're looking for are inside a div with id "main-content"
# Terms begin with an element of form p:(color)[term name]; name may be inside a nested element
# Term information immediately follows as an ul element
# Each information entry is of form li:"[info type]:[" "/""][info]" inside the containing ul; the data may be spread out across multiple subelements

# To avoid complex checks at every step of the parsing process to know where we are, TermParser will function based on a set of predefined "states".
# Each state is represented by a number, to avoid having to come up with a bunch of meaningful unique names:
# 0 - base state, parser is at a random non-interesting point in the HTML tree
# 1 - parser inside the HTML element holding all the good stuff we're interested
# 2 - inside a p that might contain a term name
# 3 - found new term name
# 4 - inside latest term info list
# 5 - inside info list item

# Desired info types
fieldnames = ["Term", "Definition", "Example(s)", "Usage"]

# Desired colors
colors = ["rgb(0,0,255)", "rgb(255,153,0)"]

# getColor returns the color of the style attribute, if present
# returns an empty string otherwise
# assumes the color is the first style attribute
def getColor(attrs):
    for attr in attrs:
        if attr[0] == "style":
            # looking for a style of form "color: [color];" or at least starting this way
            if len(attr[1]) >= 9 and attr[1][:7] == "color: ":
                i = attr[1].find(";")
                return attr[1][7:i]
    return ""

class TermParser(HTMLParser):
    branch = [] # keep track of where we are inside the containing element
    state = 0 # keeps track of conditions that would require complex evaluation at the current step
    
    terms = []
    
    color = "" # current branch color
    data = "" # cumulated data from current list item
    
    def handle_starttag(x, tag, attrs):
        if len(x.branch) == 0:
            # looking for container div
            if tag == "div" and len(attrs) > 0 and attrs[0][0] == "id" and attrs[0][1] == "main-content":
                x.branch.append(tag)
                x.state = 1

        else:
            x.branch.append(tag)
            
            if x.state == 1 and x.branch == ["div", "p"]:
                x.color = getColor(attrs)
                x.data = ""
                x.state = 2

            elif x.state == 2:
                # color of nested elements override the old one
                color = getColor(attrs)
                if color != "":
                    if x.data != "" and color != x.color:
                        # reject color change in middle of data
                        x.state = 1
                        return
                    x.color = color

            elif x.state == 3 and len(x.branch) == 2:
                if tag == "ul":
                    # entered info list
                    x.state = 4

                else:
                    # no following ul -> term with no info -> move on
                    x.state = 1

            elif x.state == 4 and x.branch == ["div", "ul", "li"]:
                # entered info list item
                x.data = ""
                x.state = 5


    def handle_data(x, data):
        if x.state == 2:
            # inside a potential new term element
            if x.data != "" or x.color not in colors:
                # reject multipart data or wrong colors
                x.state = 1
                return

            x.data = data

        elif x.state == 5:
            # cumulate all encountered data inside a list item
            x.data += data

    def handle_endtag(x, tag):
        # some HTML tags don't require an explicit closing tag, so we trim the branch up to the nearest match
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
                # left container
                x.state = 0

            elif x.state == 2 and len(x.branch) == 1:
                # left potential term definition element
                if x.data == "":
                    # no term name found
                    x.state = 1
                    return
                
                # add new term name
                x.terms.append({"Term": x.data})
                x.state = 3

            elif x.state == 4 and len(x.branch) == 1:
                # left info list
                x.state = 1

            elif x.state == 5 and len(x.branch) == 2:
                # left info list item
                x.state = 4
                
                # add cumulated info to latest term

                # determine info type
                i = x.data.find(":")
                if i == -1 or i == len(x.data)-1:
                    # unexpected term info structure -> move on
                    return

                typ = x.data[:i]
                i += 1 # skip the ":"
                if x.data[i] == " ":
                    if len(x.data) < i + 2:
                        # info is just an empty space -> skip whole item
                        return
                    # skip empty space
                    i += 1
                
                info = x.data[i:]
                x.addInfo(typ, info)
    
    # addInfo adds a new info entry or appends to the last element in terms
    def addInfo(x, typ, info):
        if typ not in fieldnames:
            return

        n = len(x.terms) - 1
        term = x.terms[n]

        if typ in term:
            # append info to existing type
            term[typ] += "\n" + info
        
        else:
            # add new info type
            term[typ] = info

        # this might not be necessary as python might work with dictionary references, but just in case
        x.terms[n] = term

parser = TermParser()

# parse html file
f = open("terminology.html", "r", encoding="utf-8")
parser.feed(f.read())
f.close()

# write csv file
f = open("terminology.csv", "w", encoding="utf-8", newline="")

w = csv.DictWriter(f, fieldnames=fieldnames)

w.writeheader()
for term in parser.terms:
    w.writerow(term)

f.close()
