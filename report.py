import os
import sys
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class bcolors:
	GREEN = '\033[92m'
	RED = '\033[91m'
	BLUE = '\033[94m'
	YELLOW = '\033[93m'
	ENDC = '\033[0m'

folder = sys.argv[1]

def response(folder, results):
	for output in os.listdir(folder):
		if output != "header":
			with open(f"{folder}/{output}") as resFile:
				resArray = resFile.readlines()
			resFile.close()
		resArray = map(lambda s: s.strip(), resArray)

		for x in resArray:
			injectlist = f'<li class="list-group-item align-items-start justify-content-between" value="{x}" style="display:flex;"><div class="ms-2 me-auto"><div class="fw-bold">{x}</div><code></code></div></li>'
			output = output.split(".")[0].upper()
			if output in results["curl"]:
				results["curl"][output] += [injectlist]
			else:
				results["curl"][output] = [injectlist]
	folder = folder + '/header'
	for site in os.listdir(folder):
		with open(f"{folder}/{site}") as resFile:
			resArray = resFile.readlines()
		resFile.close()
		resArray = map(lambda s: s.strip(), resArray)
		
		status = "UNKNOWN"
		server = "UNKNOWN"
		version = "UNKNOWN"
		xframe = "IFRAME"
		location = ""
		cors = ""
		
		ssl = site.split(":")[0]
		site = site.split(":")[1]

		if ssl =='http':
			ussl = f'<span class="badge text-bg-danger">{ssl.upper()}</span>'
		else:
			ussl = ""	#f'<span class="badge text-bg-success">{ssl.upper()}</span>'

		for x in resArray:
			x = x.lower()
			if x.startswith("http/"):
				status = x.split(" ")[1]
				version = x.split(" ")[0].split("/")[1].upper()
				
			if x.startswith("server: "):
				server = x.split(": ")[1].upper()
					
			if x.startswith("location: "):
				location = x.split(": ")[1]
				
			if x.startswith("x-frame-options: "):
				xframe = x.split(": ")[1].upper()
				
			if x.startswith("access-control-"):
				cors = '<span class="badge text-bg-warning">CORS</span>'
				
		href = f"{ssl}://{site}"
		
		if xframe == 'IFRAME':
			uxframe = f'<span class="badge text-bg-info">IFRAME</span>'
		else:
			uxframe = ""
			
		
		if status.startswith("3"):
			if location.startswith("/"):
				location = location
			else:
				location = urlparse(location).netloc
			site = f'{site} → {location}'
			
			
		checks = {
			"CORS":[cors, '<span class="badge text-bg-warning">CORS</span>'],
			"INSECURE":[ssl, "http"]
		}
		
		injectlist = f'<li class="list-group-item align-items-start justify-content-between" value="{href}" style="display:flex;"><div class="ms-2 me-auto"><div class="fw-bold"><a href="{href}" target="_blank" rel="noopener noreferrer">{site}</a></div><code>HTTP/{version} {status} {server}</code></div>{ussl}{uxframe}{cors}</li>'
		
		for item in checks:
			if checks[item][0] == checks[item][1]:
				if item in results["vulnerable"]:
					results["vulnerable"][item] += [injectlist]
				else:
					results["vulnerable"][item] = [injectlist]

		
		if status in results["status"]:
			results["status"][status] += [injectlist]
			
		else:
			results["status"][status] = [injectlist]
		
		if server in results["server"]:
			results["server"][server] += [injectlist]

		else:
			results["server"][server] = [injectlist]

		if xframe in results["iframe"]:
			results["iframe"][xframe] += [injectlist]

		else:
			results["iframe"][xframe] = [injectlist]
			
		version = 'HTTP/' + version

		if version in results["version"]:
			results["version"][version] += [injectlist]

		else:
			results["version"][version] = [injectlist]


			
results = {
	"status":{},
	"server":{},
	"iframe":{},
	"version":{},
	"vulnerable":{},
	"curl":{}
}

response(folder, results)

for option in results:
	results[option] = dict(sorted(results[option].items(), key=lambda item: item[0])) 
	

html = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-Zenh87qX5JnK2Jl0vWa8Ck2rdkQ2Bzep5IDxbcnCeuOxjzrPF/et3URy9Bv1WTRi" crossorigin="anonymous">
  </head>
  <style>
    :root {
      --theme-bg: #1f1f1f;
      --theme-sec: #2a2a2a;
      --theme-btn: #20c997;
    }

    /* width */
    ::-webkit-scrollbar {
      width: 10px;
    }

    /* Track */
    ::-webkit-scrollbar-track {
      background: var(--theme-bg);
    }

    /* Handle */
    ::-webkit-scrollbar-thumb {
      background: #444;
    }

    /* Handle on hover */
    ::-webkit-scrollbar-thumb:hover {
      background: #333;
    }

    body {
      background-color: var(--theme-bg);
      color: white;
    }

    .badge,
    code {
      border-radius: 0;
    }

    a {
      text-decoration: none;
      color: inherit;
    }

    ol {
      height: 67.5vh;
      overflow: hidden;
      overflow-y: scroll;
      border: 0;
    }

    .nav-link {
      font-weight: bold;
    }

    .tab-border {
      border: 2.5px solid var(--theme-btn);
    }

    .nav-pills .nav-link {
      color: var(--theme-btn);
      border: 0;
      border-radius: 0;
    }

    .list-group-item {
      background-color: var(--theme-bg);
      color: white;
      border-color: var(--theme-sec);
    }

    .nav-pills .nav-link.active,
    .nav-pills .show>.nav-link {
      color: white;
      background-color: var(--theme-btn);
    }

    h4 {
      font-weight: 900;
      text-shadow: 1px 1px var(--theme-btn);
    }

    .count {
      top: 5px;
      left: 40px;
    }

    .btn-success {
      background-color: var(--theme-btn);
      border: 0;
    }

    .form-control {
      background-color: var(--theme-sec);
      border-color: var(--theme-sec);
      color: white;
      margin-right: 15px;
    }

    .form-control:focus {
      background-color: var(--theme-sec);
      border-color: var(--theme-sec);
      color: white;
    }

    .bottom-menu {
      padding: 10px 15px;
    }

    .nav-tabs .nav-item.show .nav-link,
    .nav-tabs .nav-link.active {
      color: var(--theme-btn);
      background-color: var(--theme-sec);
      border-color: var(--theme-sec);
      border-top: 3px solid var(--theme-sec);
      border-bottom: 3px solid var(--theme-btn);
    }

    .nav-tabs .nav-link {
      margin: 0;
      background: var(--theme-bg);
      border: 0;
      border-radius: 0;
      color: var(--theme-btn);
      border-top: 3px solid var(--theme-sec);
      border-bottom: 3px solid var(--theme-sec);
      margin-bottom: -3px;
    }

    .nav-tabs .nav-link:hover {
      background: var(--theme-bg);
      color: var(--theme-btn);
      border-top: 3px solid var(--theme-sec);
      border-bottom: 3px solid var(--theme-btn);
    }

    .nav-tabs {
      border-bottom: 3px solid var(--theme-sec);
    }

    a:hover {
      color: white;
    }

    a:focus {
      color: var(--theme-btn);
    }
  </style>
  <body class="container" style="margin-top:5vh;">
    <div class="d-flex justify-content-between">
      <h4>HTTP BUSTER</h4>
      <ul class="nav nav-pills justify-content-end" id="pills-tab" role="tablist">

      </ul>
    </div>
    <div class="tab-content" id="pills-tabContent">

    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-OERcA2EqjJCMA+/3y+gxIOqMEjwtxJY7qPCqsdltbNJuaOe923+mo//f6V8Qbsw3" crossorigin="anonymous"></script>
    <script src="https://code.jquery.com/jquery-3.6.1.min.js" integrity="sha256-o88AwQnZB+VDvE9tvIXrMQaPlFFSUTR+nldQm1LuPXQ=" crossorigin="anonymous"></script>
  </body>
  <script class="jquery"></script>
</html>
"""

soup = BeautifulSoup(html, "html.parser")

icon = """
<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px" fill="white">
  <path d="M0 0h24v24H0z" fill="none" />
  <path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" />
</svg>
"""

#using double backslash to escpae string format in paython
jquery = """
$("#input-custom").on("keyup", function() {
    {
        var value = $(this).val().toLowerCase();
        $("#list-custom li").filter(function() {
            {
                $(this).toggle($(this).attr("value").toLowerCase().indexOf(value) > -1)
            }
        });
    }
});
$("#copy-custom").click(function() {
    {
        const copylist = $.map($("#list-custom > li"), li => $(li).attr("value"));
        navigator.clipboard.writeText(copylist.join("\\r"));
    }
});
"""

for item in results:
	if len(results[item]):
		print(f"\n{item.upper()}:", end =" ")
	else:
		continue
	soup.find("ul", {"id": "pills-tab"}).append(BeautifulSoup(f'<li class="nav-item" role="presentation"><button class="nav-link" id="pills-{item}-tab" data-bs-toggle="pill" data-bs-target="#pills-{item}" type="button" role="tab" aria-controls="pills-{item}" aria-selected="false">{item.upper()}</button></li>', 'html.parser'))
	soup.find("div", {"id": "pills-tabContent"}).append(BeautifulSoup(f'<div class="tab-pane fade tab-border" id="pills-{item}" role="tabpanel" aria-labelledby="pills-{item}-tab" tabindex="0"><nav><div class="nav nav-tabs justify-content-center {item}-tab" id="nav-tab" role="tablist"></div></nav><div class="tab-content {item}-content" id="nav-tabContent"></div></div>', 'html.parser'))
	for option in results[item]:
		results[item][option].sort()
		count = len(results[item][option])
		print(f"{bcolors.YELLOW}{option}{bcolors.ENDC}:{bcolors.GREEN}{count}{bcolors.ENDC}", end =" ")
		optionsave = option
		option = option.replace("/", "-").replace(" ","-").replace(".","-").replace("(","-").replace(")","-")
		soup.find("script", {"class": "jquery"}).append(BeautifulSoup(jquery.replace("custom", f"{option}"), 'html.parser'))
		search = f'<input class="form-control" id="input-{option}" type="text" placeholder="Search">'
		copy = f'<button type="button" class="btn btn-success position-relative" id="copy-{option}">{icon}<span class="position-absolute translate-middle badge rounded-pill bg-primary count">{count}</span></button>'
		soup.find("div", {"class": f"{item}-tab"}).append(BeautifulSoup(f'<button class="nav-link" id="nav-{option}-tab" data-bs-toggle="tab" data-bs-target="#nav-{option}" type="button" role="tab" aria-controls="nav-{option}" aria-selected="false">{optionsave}</button>', 'html.parser'))
		soup.find("div", {"class": f"{item}-content"}).append(BeautifulSoup(f'<div class="tab-pane fade content-update" id="nav-{option}" role="tabpanel" aria-labelledby="nav-{option}-tab" tabindex="0"><ol class="list-group list-group-numbered list-{option} list-group-flush" id="list-{option}"></ol><div class="d-flex justify-content-between bottom-menu">{search}{copy}</div></div>', 'html.parser'))
		for content in results[item][optionsave]:
			soup.find("ol", {"class": f"list-{option}"}).append(BeautifulSoup(content, 'html.parser'))

	try:
		pillupdate = soup.find("ul", {"id": "pills-tab"}).li.button
		pillupdate['class'] = pillupdate.get('class', []) + ['active']
		pillupdate['aria-selected'] = 'true'
		
		pilltabupdate = soup.find("div", {"id": "pills-tabContent"}).div
		pilltabupdate['class'] = pilltabupdate.get('class', []) + ['show active']
		
		tabupdate = soup.find("div", {"class": f"{item}-tab"}).button
		tabupdate['class'] = tabupdate.get('class', []) + ['active']
		tabupdate['aria-selected'] = 'true'
	
		contentupdate = soup.find("div", {"class": f"{item}-content"}).div
		contentupdate['class'] = contentupdate.get('class', []) + ['show active']
	except Exception:
		pass

with open(f"report.html", 'w') as outlist:
	outlist.write(str(soup))
outlist.close()
