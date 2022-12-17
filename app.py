from flask import Flask, request, jsonify
from search import search
from filter import Filter
from storage import DBStorage
import html
#from .index import images

app = Flask(__name__)

styles = """
<style>
    .site {
        font-size: .8rem;
        color: green;
    }
    
    .snippet {
        font-size: .9rem;
        color: gray;
        margin-bottom: 30px;
    }
    
    .rel-button {
        cursor: pointer;
        color: blue;
    }
    *{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Poppins', sans-serif;
}

.container{
    width: 100%;
    min-height: 100vh;
    padding: 5%;
    background-image: linear-gradient(rgba(0,8,51,0.9),rgba(0,8,51,0.9)),url(images/bg.jpg);
    background-position: center;
    background-size: cover;
    display: flex;
    align-items: center;
    justify-content: center;
}

.search-bar{
    width: 100%;
    max-width: 700px;
    background: rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    border-radius: 60px;
    padding: 10px 20px;
    backdrop-filter: blur(4px) saturate(180%);
}

.search-bar input{
    background: transparent;
    flex: 1;
    border: 0;
    outline: none;
    padding: 24px 20px;
    font-size: 20px;
    color: #cac7ff;
}

::placeholder{
    color: #cac7ff;

}

.search-bar button img{
    width: 25px;
    
}

.search-bar button{
    border: 0;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    background: #58629b;
    cursor: pointer;
}
</style>
<script>
const relevant = function(query, link){
    fetch("/relevant", {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
           "query": query,
           "link": link
          })
        });
}
</script>
"""

search_template = styles + """
    <!DOCTYPE html>
<html lang="en">
    <head>
        <title>
            Search Bar
        </title>
        <link rel="stylesheet" href="style2.css" />
        
    </head>
    <body>
    <div class="container">

    

<form action="/" method="post" class="search-bar">
    <input type="text" placeholder="Search..." name="query">
    <button type="submit" value="Search"> <img src="images/searchicon.png"></button>
  </form> 
</div>
</body>
</html>
    """

result_template = """
<p class="site">{rank}: {link} <span class="rel-button" onclick='relevant("{query}", "{link}");'>Relevant</span></p>
<a href="{link}">{title}</a>
<p class="snippet">{snippet}</p>
"""

def show_search_form():
    return search_template

def run_search(query):
    results = search(query)
    fi = Filter(results)
    filtered = fi.filter()
    rendered = search_template
    filtered["snippet"] = filtered["snippet"].apply(lambda x: html.escape(x))
    for index, row in filtered.iterrows():
        rendered += result_template.format(**row)
    return rendered

@app.route("/", methods=['GET', 'POST'])
def search_form():
    if request.method == 'POST':
        query = request.form["query"]
        return run_search(query)
    else:
        return show_search_form()

@app.route("/relevant", methods=["POST"])
def mark_relevant():
    data = request.get_json()
    query = data["query"]
    link = data["link"]
    storage = DBStorage()
    storage.update_relevance(query, link, 10)
    return jsonify(success=True)