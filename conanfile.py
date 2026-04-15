from conan import ConanFile, tools
from conan.tools.files import copy, apply_conandata_patches, export_conandata_patches, get, collect_libs
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.cmake import CMakeToolchain, CMakeDeps
from conan.tools.scm import Git
from os.path import join

required_conan_version = ">=2.0.6"
class NvbloxRecipe(ConanFile):
    name = "eiva-nvblox"
    version = "0.0.9"
    license = "Apache-2.0"
    author = "Nvidia"
    url = "https://github.com/nvidia-isaac/nvblox.git"
    description = "GPU SDF Library"
    topics = ("Nvidia", "nvblox", "voxel", "mesh", "esdfs")
    settings = "os", "compiler", "build_type", "arch"
    package_type = "library"

    options = {
        "shared": [True, False]
    }

    default_options = {
        "shared": True
    }

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def requirements(self):
        self.requires("benchmark/1.9.4")
        self.requires("eigen/3.4.0a")
        self.requires("gflags/2.2.2")
        self.requires("glog/0.5.0")
        self.requires("sqlite3/3.50.4")
        self.requires("eiva-stdgpu/cci.20241126")
        self.requires("gtest/1.17.0")
        
    def build_requirements(self):
        pass
    
    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        
        self.options["eigen"].shared = False
        # OSS license safety
        # options eigen
        self.options["eigen"].MPL2_only = True
        
        self.options["glog"].with_gflags = False

    def generate(self):
        tc = CMakeToolchain(self, generator="Ninja")
        tc.preprocessor_definitions["NOMINMAX"] = ""
        tc.variables["BUILD_TESTING"] = True
        tc.variables["BUILD_BENCHMARKS"] = False
        tc.variables["BUILD_EXPERIMENTS"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_EXECUTABLES"] = False
        tc.variables["BUILD_PYTORCH_WRAPPER"] = False
        tc.variables["USE_SYSTEM_BENCHMARK"] = True
        tc.variables["USE_SYSTEM_EIGEN"] = True
        tc.variables["USE_SYSTEM_GFLAGS"] = True
        tc.variables["USE_SYSTEM_GLOG"] = True
        tc.variables["USE_SYSTEM_GTEST"] = True
        tc.variables["USE_SYSTEM_SQLITE3"] = True
        tc.variables["USE_SYSTEM_STDGPU"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.set_property("cmake_file_name", "nvblox")
        self.cpp_info.set_property("cmake_target_name", "nvblox")
 

    def package(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        
        if self.settings.os == "Windows":
            # Copy PDB files for Windows builds
            copy(self, "*.pdb", join(self.build_folder, "lib"), join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.pdb", join(self.build_folder, "bin"), join(self.package_folder, "bin"), keep_path=False)
        
        # Needed for conan create package. Also works with linux
        copy(self, pattern="*.h*", src=join(self.source_folder, "include"), dst=join(self.package_folder, "include"))
        copy(self, pattern="*.a", src=self.build_folder, dst=join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="*.so", src=self.build_folder, dst=join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="*.lib", src=self.build_folder, dst=join(self.package_folder, "lib"), keep_path=False)
        copy(self, pattern="*.dll", src=self.build_folder, dst=join(self.package_folder, "bin"), keep_path=False)
        copy(self, pattern="*.dylib", src=self.build_folder, dst=join(self.package_folder, "lib"), keep_path=False)
            
        
    def export_sources(self):
        export_conandata_patches(self)