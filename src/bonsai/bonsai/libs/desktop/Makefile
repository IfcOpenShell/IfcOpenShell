# Linux Makefile for installing GUI desktop files, icons and ifc file associations

DESTDIR = ${HOME}/.local

install :
	mkdir -p \
	${DESTDIR}/bin \
	${DESTDIR}/share/icons/hicolor/128x128/apps \
	${DESTDIR}/share/icons/hicolor/128x128/mimetypes \
	${DESTDIR}/share/applications \
	${DESTDIR}/share/mime/packages
	cp bonsai ${DESTDIR}/bin/
	chmod +x ${DESTDIR}/bin/bonsai
	cp bonsai.png ${DESTDIR}/share/icons/hicolor/128x128/apps/
	cp bonsai.desktop ${DESTDIR}/share/applications/
	cp bonsai.xml ${DESTDIR}/share/mime/packages/
	cp x-ifc_128x128.png ${DESTDIR}/share/icons/hicolor/128x128/mimetypes/x-ifc.png
	update-mime-database ${DESTDIR}/share/mime/ || true
	update-desktop-database ${DESTDIR}/share/applications/ || true

uninstall :
	rm -f \
	${DESTDIR}/bin/bonsai \
	${DESTDIR}/share/icons/hicolor/128x128/apps/bonsai.png \
	${DESTDIR}/share/applications/bonsai.desktop \
	${DESTDIR}/share/mime/packages/bonsai.xml \
	${DESTDIR}/share/icons/hicolor/128x128/mimetypes/x-ifc.png
	update-mime-database ${DESTDIR}/share/mime/ || true
	update-desktop-database ${DESTDIR}/share/applications/ || true
