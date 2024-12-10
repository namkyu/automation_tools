import sys
import xml.dom.minidom

class MavenToGradle:

    def __init__(self, pom_file_path, style):
        self.pom_file_path = pom_file_path
        self.style = style

    def execute(self):
        dom_tree = xml.dom.minidom.parse(self.pom_file_path)
        collection = dom_tree.documentElement

        dependencies = collection.getElementsByTagName("dependency")
        for dependency in dependencies:
            group_id = self.get_data(dependency.getElementsByTagName('groupId'))
            artifact_id = self.get_data(dependency.getElementsByTagName('artifactId'))
            version = self.get_data(dependency.getElementsByTagName('version'))
            scope = self.get_data(dependency.getElementsByTagName('scope'))

            if scope == "test":
                self.make_gradle_dependency("testImplementation", group_id, artifact_id, version)
            elif scope == "compile":
                self.make_gradle_dependency("compileOnly", group_id, artifact_id, version)
            elif scope == "runtime":
                self.make_gradle_dependency("runtimeOnly", group_id, artifact_id, version)
            elif scope == "provided" or artifact_id == "lombok":
                self.make_gradle_dependency("compileOnly", group_id, artifact_id, version)
                self.make_gradle_dependency("annotationProcessor", group_id, artifact_id, version)
            else:
                self.make_gradle_dependency("implementation", group_id, artifact_id, version)

    def get_data(self, tag):
        if tag.length == 0:
            return None
        return tag[0].firstChild.data

    @staticmethod
    def enum(*sequential, **named):
        enums = dict(zip(sequential, range(len(sequential))), **named)
        return type('Enum', (), enums)

    def make_gradle_dependency(self, dependency_type, group, name, version):
        if self.style.lower() == "common":
            if version is None:
                print("%s(group: '%s', name: '%s')" % (dependency_type, group, name))
            else:
                print("%s(group: '%s', name: '%s', version: '%s')" % (dependency_type, group, name, version))
        elif self.style.lower() == "short":
            if version is None:
                print("%s '%s:%s'" % (dependency_type, group, name))
            else:
                print("%s '%s:%s:%s'" % (dependency_type, group, name, version))


# ===========================================
# main
# ===========================================
if __name__ == "__main__":
    argument_len = len(sys.argv)
    if argument_len != 3:
        print("invalid argument length !!")
        sys.exit(1)

    m = MavenToGradle(sys.argv[1], sys.argv[2])
    m.execute()
