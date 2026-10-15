# Variables shared by `src/*/Makefile`, included as `include ../vars.mk`.

SHELL := sh
IS_STABLE:=FALSE

VERSION:=$(shell cat ../../VERSION)
VERSION_BASE:=$(shell sed -E 's/[[:alpha:]]+[0-9]+$$//' ../../VERSION)
VERSION_PYTHON:=$(shell sed -e 's/alpha/a/' -e 's/post/.post/' ../../VERSION)
VERSION_SEMVER:=$(shell sed -E 's/([[:alpha:]]+)([0-9]+)$$/-\1\2/' ../../VERSION)
VERSION_DATE:=$(shell date '+%y%m%d')
VERSION_DAILY:=$(VERSION_BASE)a$(VERSION_DATE)
VERSION_SEMVER_DAILY:=$(VERSION_BASE)-alpha$(VERSION_DATE)

PYTHON:=python3
PIP:=pip3
SED:=sed -i
VENV_BIN:=bin

ifeq ($(OS),Windows_NT)
PYTHON:=python
PIP:=pip
VENV_BIN:=Scripts
else
UNAME_S:=$(shell uname -s)
ifeq ($(UNAME_S),Darwin)
SED:=sed -i '' -e
endif
endif

VENV_ACTIVATE:=$(VENV_BIN)/activate
