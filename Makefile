.PHONY: setup run eval clean deploy

setup:
	python setup.py

run:
	python main.py

eval:
	python -m scripts.evaluator

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

deploy:
	docker build -t carrec-ai .
