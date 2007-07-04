# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#


%define _with_gcj_support 1
%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define _without_maven 1

# If you don't want to build with maven, and use straight ant instead,
# give rpmbuild option '--without maven'
%define with_maven %{!?_without_maven:1}%{?_without_maven:0}
%define without_maven %{?_without_maven:1}%{!?_without_maven:0}

Name:           maven-jxr
Version:        1.0
Release:        %mkrel 2.2.1
Epoch:          0
Summary:        Source cross referencing tool
License:        Apache Software License
Group:          Development/Java
URL:            http://maven.apache.org/doxia/

Source0:        %{name}-%{version}.tar.gz
# svn export http://svn.apache.org/repos/asf/maven/jxr/tags/maven-jxr-1.0/
#    maven-jxr/
# tar czf maven-jxr.tar.gz maven-jxr/
Source1:        %{name}-jpp-depmap.xml
Source2:        %{name}-build.xml

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%if ! %{gcj_support}
BuildArch:      noarch
%endif

BuildRequires:  jpackage-utils >= 0:1.7.2
%if %{with_maven}
BuildRequires:  maven2 >= 2.0.4
BuildRequires:  maven2-plugin-resources
BuildRequires:  maven2-plugin-compiler
BuildRequires:  maven2-plugin-resources
BuildRequires:  maven2-plugin-compiler
BuildRequires:  maven2-plugin-surefire
BuildRequires:  maven2-plugin-jar
BuildRequires:  maven2-plugin-install
BuildRequires:  maven2-plugin-javadoc
%else
BuildRequires:  ant, ant-nodeps
%endif
BuildRequires:  junit >= 3.8.2
BuildRequires:  jakarta-commons-collections >= 3.1
BuildRequires:  oro >= 2.0.8
BuildRequires:  plexus-utils >= 1.2
BuildRequires:  velocity >= 1.4

Requires:       junit >= 3.8.2
Requires:       jakarta-commons-collections >= 3.1
Requires:       oro >= 2.0.8
Requires:       plexus-utils >= 1.2
Requires:       velocity >= 1.4

Requires(post):    jpackage-utils >= 0:1.7.2
Requires(postun):  jpackage-utils >= 0:1.7.2

%if %{gcj_support}
BuildRequires:          java-gcj-compat-devel
Requires(post):         java-gcj-compat
Requires(postun):       java-gcj-compat
%endif

%description
Maven JXR is a source cross referencing tool.

%if %{with_maven}
%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
Javadoc for %{name}.
%endif

%prep
%setup -q -n %{name}
cp -p %{SOURCE2} build.xml

%build

export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mkdir -p $MAVEN_REPO_LOCAL

%if %{with_maven}

    mvn-jpp \
        -e \
        -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        -Dmaven2-jpp.depmap.file=%{SOURCE1} \
        install javadoc:javadoc

%else

mkdir lib
build-jar-repository -s -p lib/ \
                        commons-collections \
                        oro \
                        plexus/utils \
                        velocity

%{ant} -Dmaven.mode.offline=true

%endif

%install
rm -rf $RPM_BUILD_ROOT
# jars/poms
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}/%{name}
install -d -m 755 $RPM_BUILD_ROOT/%{_datadir}/maven2/poms

install -pm 644 target/%{name}-%{version}.jar \
                $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
%add_to_maven_depmap org.apache.maven maven-jxr %{version} JPP %{name}

install -pm 644 pom.xml $RPM_BUILD_ROOT/%{_datadir}/maven2/poms/JPP.%{name}.pom

(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; \
  do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)

%if %{with_maven}
# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}

cp -pr target/site/apidocs/* \
                $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}/

ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}
%endif

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_maven_depmap

%if %{gcj_support}
%{update_gcjdb}
%endif

%postun
%update_maven_depmap

%if %{gcj_support}
%{clean_gcjdb}
%endif

%files
%defattr(-,root,root,-)
%{_javadir}
%{_datadir}/maven2
%config(noreplace) %{_mavendepmapfragdir}/*

%if %{gcj_support}
%dir %attr(-,root,root) %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/maven-jxr-1.0.jar.*
%endif

%if %{with_maven}
%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/*
%endif
