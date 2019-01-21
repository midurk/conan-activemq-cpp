#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os, tempfile


class AcitvemqCppConan(ConanFile):
    name = "activemq-cpp"
    version = "3.9.4"
    description = "CMS (stands for C++ Messaging Service) is a JMS-like API for C++ for interfacing with Message Brokers such as Apache ActiveMQ."

    topics = ("messaging", "queue", "activemq")

    url = "https://github.com/midurk/activemq-cpp"
    homepage = "http://activemq.apache.org/cms"
    author = "Michal Durkovic <michal.durkovic@innovatrics.com>"
    license = "Apache-2.0"
    exports = ["LICENSE.md"]

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "with_openssl": [True, False]}
    default_options = {"shared": False, "fPIC": True, "with_openssl": True}

    # Custom attributes for Bincrafters recipe conventions
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = ( "apr/1.6.5@mdurkovic/testing", )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def requirements(self):
        if self.options.with_openssl:
            self.requires("OpenSSL/1.0.2q@conan/stable")

    def source(self):
        source_url = "http://tux.rainside.sk/apache/activemq"
        tools.get("{0}/{1}/{2}/{1}-library-{2}-src.tar.gz".format(source_url, self.name, self.version), sha256="7390b0266baf1291e66b34b9a52770de7cbdb26dab4217b4921cbc220ef4b08f")
        extracted_dir = "{0}-library-{1}".format(self.name, self.version)

        os.rename(extracted_dir, self._source_subfolder)

    def _build_with_autotools(self):
        build_env = AutoToolsBuildEnvironment(self)
        build_env.fpic = self.options.fPIC
        with tools.environment_append(build_env.vars):
            with tools.chdir(self._source_subfolder):
                configure_args = ['--prefix=%s' % self.package_folder]
                configure_args.append('--enable-shared' if self.options.shared else '--disable-shared')
                configure_args.append('--enable-static' if not self.options.shared else '--disable-static')
                configure_args.append("--with-apr=%s" % self.deps_cpp_info["apr"].rootpath)
                if self.options.with_openssl:
                    configure_args.append('--enable-ssl')
                    configure_args.append("--with-openssl=%s" % self.deps_cpp_info["OpenSSL"].rootpath)
                else:
                    configure_args.append('--disable-ssl')
                build_env.configure(args=configure_args)
                build_env.make(args=["-s", "all"])
                build_env.make(args=["-s", "install"])

    def build(self):
        self._build_with_autotools()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = [ os.path.join("include", "{0}-{1}".format(self.name, self.version)) ]
