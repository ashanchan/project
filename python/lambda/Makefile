PROJECT = lambda
VIRTUAL_ENV = env
FUNCTION_NAME = testMyLambda
AWS_REGION = us-east-1
FUNCTION_HANDLER = lambda_handler
LAMBDA_ROLE = arn:aws:iam::865376845454:role/service-role/myLambdaFunction-role-gfqpfviv

install : virtual
build : build_package_tmp zip

virtual :
	@echo '--> Setup and activate virtual env'
	if test ! -d '$(VIRTUAL_ENV)' ; then \
		pip install virtualenv; \
		virtualenv $(VIRTUAL_ENV);\
	fi
	@echo ''

clean_package :
	rm -f ./package/*/**	

build_package_tmp:
	mkdir -p ./package/tmp/lib 
	cp -a ./$(PROJECT)/. ./package/tmp/

zip:
	cd ./package/tmp && zip -r ../$(PROJECT).zip .
