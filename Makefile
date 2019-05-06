.PHONY: default
defaul: dev

SCRAPE_DATA = fass.jsonl.gz
SCRAPER_REPO = fass-scrape
SCRAPER_REPO_URL = https://github.com/molobrakos/$(SCRAPER_REPO)

$(SCRAPER_REPO):
	git clone $(SCRAPER_REPO_URL)

$(SCRAPE_DATA): | $(SCRAPER_REPO)
	cd $(SCRAPER_REPO) && make
	cp $(SCRAPE_DATA) ..

.PHONY: dev
dev: $(SCRAPE_DATA)
	docker-compose build app-dev
	zcat $(SCRAPE_DATA) | docker-compose run app-dev python3 main.py

.PHONY: cluster
cluster: $(SCRAPE_DATA)
	docker-compose build app-cluster
	zcat $(SCRAPE_DATA) | docker-compose run app-cluster python3 main.py

.PHONY: clean
clean:
	docker-compose down -v --remove-orphans

.PHONY: setup
setup:
	sudo sysctl -w vm.max_map_count=262144 
