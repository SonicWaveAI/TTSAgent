.PHONY: run
run:  ## 运行服务
	@echo "running server..."
	@source $(CURDIR)/venv/bin/activate && python3 run.py

help:
	@awk -F ':|##' '/^[^\t].+?:.*?##/ {\
		printf "\033[36m%-30s\033[0m \033[31m%s\033[0m\n", $$1, $$NF \
	}' $(MAKEFILE_LIST)
.DEFAULT_GOAL=help
.PHONY=help