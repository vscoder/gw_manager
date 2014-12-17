# $FreeBSD$

# Created by: Koloskov Alexey <koloskov@flexline.ru>

PORTNAME=		gwman
PORTVERSION=	0.9
CATEGORIES=		net-mgmt python
PKGNAMEPREFIX=	${PYTHON_PKGNAMEPREFIX}

USES=			python:2
USE_PYTHON=		autoplist distutils

#PYDISTUTILS_INSTALLARGS+=	--install-purelib=${PYTHON_SITELIBDIR} \
#							--install-data=${ETCDIR}
PYDISTUTILS_PKGVERSION=		${PORTVERSION}

MASTER_SITES=	http://192.168.20.25:8000/

MAINTAINER=koloskov@flexline.ru
COMMENT=Manage gateway

NO_BUILD=		yes

RUN_DEPENDS=    ${PYTHON_PKGNAMEPREFIX}bottle>0:${PORTSDIR}/www/py-bottle \
				${PYTHON_PKGNAMEPREFIX}daemon>0:${PORTSDIR}/devel/py-daemon \
				${PYTHON_PKGNAMEPREFIX}libdnet>0:${PORTSDIR}/net/py-libdnet \
				${PYTHON_PKGNAMEPREFIX}MySQLdb51>0:${PORTSDIR}/databases/py-MySQLdb51

USE_RC_SUBR=	gwman_server \
				gwman_agent

#PLIST_SUB+=		WWWDIR=${WWWDIR}
#WWWDIR=			${PREFIX}/www/${PORTNAME}

#FILES=			${WRKSRC}/www/conf/forms.conf \
#				${WRKSRC}/www/log/ \
#				${WRKSRC}/www/views/*.tpl

#post-patch:
	

.include <bsd.port.mk>
