VERSION:=`date '+%y%m%d'`

.PHONY: dist
dist:
	rm -rf dist
	mkdir -p dist/ifcsverchok
	cp -r ./*.py dist/ifcsverchok/
	cp -r ./nodes dist/ifcsverchok/
	cd dist/ifcsverchok && sed -i "s/999999/$(VERSION)/" __init__.py
	cd dist && zip -r ifcsverchok-$(VERSION).zip ./*
	rm -rf dist/ifcsverchok

.PHONY: clean
clean:
	rm -rf dist
