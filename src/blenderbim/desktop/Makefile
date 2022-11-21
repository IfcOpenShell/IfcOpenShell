# Linux Makefile for installing GUI desktop files, icons and ifc file associations

DESTDIR = ${HOME}/.local

install :
	mkdir -p \
	${DESTDIR}/bin \
	${DESTDIR}/share/icons/hicolor/128x128/apps \
	${DESTDIR}/share/icons/hicolor/128x128/mimetypes \
	${DESTDIR}/share/applications \
	${DESTDIR}/share/mime/packages
	cp blenderbim.sh ${DESTDIR}/bin/
	chmod +x ${DESTDIR}/bin/blenderbim.sh
	cp blenderbim.png ${DESTDIR}/share/icons/hicolor/128x128/apps/
	cp blenderbim.desktop ${DESTDIR}/share/applications/
	cp blenderbim.xml ${DESTDIR}/share/mime/packages/
	cp x-ifc_128x128.png ${DESTDIR}/share/icons/hicolor/128x128/mimetypes/x-ifc.png
	update-mime-database ${DESTDIR}/share/mime/ || true
	update-desktop-database ${DESTDIR}/share/applications/ || true

uninstall :
	rm -f \
	${DESTDIR}/bin/blenderbim.sh \
	${DESTDIR}/share/icons/hicolor/128x128/apps/blenderbim.png \
	${DESTDIR}/share/applications/blenderbim.desktop \
	${DESTDIR}/share/mime/packages/blenderbim.xml \
	${DESTDIR}/share/icons/hicolor/128x128/mimetypes/x-ifc.png
	update-mime-database ${DESTDIR}/share/mime/ || true
	update-desktop-database ${DESTDIR}/share/applications/ || true
