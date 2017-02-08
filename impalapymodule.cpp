#include "impalapymodule.h"


#include <string>
#include <vector>
#include <ios>
#include <sstream>

#include <impala/impala.h>
#include <impala/ast.h>
#include <impala/cgen.h>
#include <thorin/be/llvm/llvm.h>


class ImpalaModule::Private {
public:
	std::string name;
	std::vector<std::string> flags;
	impala::Init init;
	impala::Items items;
	bool nossa;
	int opt;
	bool debug;

	Private(char* module_name)
		: init(module_name),
		name(module_name),
		nossa(false),
		opt(0),
		debug(false)
	{
	}
};

ImpalaModule::ImpalaModule(char* module_name)
{
	p = new Private(module_name);
}

void ImpalaModule::addFlag(char* flag) {
	p->flags.push_back(std::string(flag));
}

void ImpalaModule::parseFile(char* filename, char* content) {
	std::istringstream file(content);
	impala::parse(p->items, file, filename);
}

bool ImpalaModule::generate() {
        auto module = std::make_unique<const impala::Module>("<unknown>", std::move(p->items));
        impala::check(p->init, module.get(), p->nossa);
        if (impala::num_errors() != 0)
		return false;
	// TODO: generate c interface
	impala::emit(p->init.world, module.get());
	return true;
}

bool ImpalaModule::emit_llvm() {
	thorin::emit_llvm(p->init.world, p->opt, p->debug);
	return true;
}

ImpalaModule::~ImpalaModule() {
	if (p) delete p;
}
