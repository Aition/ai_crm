from dify_plugin import Plugin
from provider.crm_qa import CrmQaProvider

plugin = Plugin()
plugin.register_provider(CrmQaProvider())

if __name__ == "__main__":
    plugin.run()
