.PHONY: release

release:
ifndef VERSION
	$(error VERSION is required, for example: make release VERSION=v0.4)
endif
	@test -z "$$(git status --short)" || { echo "Working tree must be clean before releasing."; exit 1; }
	@git rev-parse "$(VERSION)" >/dev/null 2>&1 && { echo "Tag $(VERSION) already exists."; exit 1; } || true
	git tag -a "$(VERSION)" -m "Release $(VERSION)"
	git push origin "$(VERSION)"
