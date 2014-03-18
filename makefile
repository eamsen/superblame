INSTALL_DIR = /usr/bin
PERMISSION_WARNING = "Don't forget the su-su-sudo!"

default:
	@echo "There is nothing to do, it's Python!"

install:
	@ln -s $(CURDIR)/superblame.py $(INSTALL_DIR)/superblame || echo $(PERMISSION_WARNING)

uninstall:
	@rm $(INSTALL_DIR)/superblame || echo $(PERMISSION_WARNING)
