import json, http.client, sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

conn = http.client.HTTPSConnection("hacker-news.firebaseio.com")
payload = "[]"
conn.request("GET", "/v0/topstories.json?print=pretty", payload)
res = conn.getresponse()
data = res.read().decode("utf-8")
data = data[2 : len(data) - 2]
data = data.split(", ")
data = [int(x) for x in data]
conn.close()
data2 = []
for x in range(10):
    conn.request("GET", "/v0/item/{}.json?print=pretty".format(data[x]), payload)
    res2 = conn.getresponse()
    res2 = res2.read().decode("utf-8")
    data2.append( json.loads(res2))
    conn.close()
for x in data2:
    if("url" in x and "title" in x and "id" in x and "by" in x):
        connection.execute('INSERT INTO articles (id, url, title, author) VALUES (?, ?, ?, ?)', (x["id"],x["url"],x["title"],x["by"]))

connection.commit()
connection.close()
