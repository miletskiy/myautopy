# Docker Management Makefile for BidReview Services

.PHONY: all pip black sort help


help:
	@echo "Available commands:"
	@echo "  all               - Start services in development mode"
	@echo "  black              - Start services in production mode"
	@echo "  sort              - Start services in production mode"


all:
	python main.py --all

pip:
	pip install -r requirements-dev.txt


black:
	black -v . src/

sort:
	isort src/ tests/ main.py
