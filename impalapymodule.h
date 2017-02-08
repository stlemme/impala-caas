
//#include <string>
//#include <vector>

//typedef std::string String;
//typedef std::vector<String> StringArray;


class ImpalaModule {
public:
	ImpalaModule(char* module_name);

	void addFlag(char* flag);
	void parseFile(char* filename, char* content);

	bool generate();
	bool emit_llvm();

	~ImpalaModule();

private:
	class Private;
	Private* p;
};
