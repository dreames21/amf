VERSION = dev-6.0.1

DEPLOY_DIR = /home/ld/Dropbox/CfA/amf/

deploy:
	@rsync -avz python $(DEPLOY_DIR)/$(VERSION)/
