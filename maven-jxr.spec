# Copyright (c) 2000-2008, JPackage Project
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

%define section   free
%define gcj_support 1
%define _without_maven 1
# If you don't want to build with maven, and use straight ant instead,
# give rpmbuild option '--without maven'
%define with_maven %{!?_without_maven:1}%{?_without_maven:0}
%define without_maven %{?_without_maven:1}%{!?_without_maven:0}

%define bname jxr

%define maven_settings_file %{_builddir}/%{name}/settings.xml

Name:           maven-jxr
Version:        2.1
Release:        %mkrel 2.0.3
Epoch:          0
Summary:        Source cross referencing tool
License:        Apache Software License 2.0
Group:          Development/Java
URL:            http://maven.apache.org/
Source0:        %{name}-%{version}.tar.gz
# svn export http://svn.apache.org/repos/asf/maven/jxr/tags/jxr-2.1/ maven-jxr-2.1
Source1:        %{name}-build.xml
Source2:        %{name}-jpp-depmap.xml
Source3:        %{name}-settings.xml
Source4:        %{name}-autogenerated-files.tar.gz
Patch0:         %{name}-maven-jxr-pom.patch
Patch1:         %{name}-maven-jxr-plugin-pom.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

%if ! %{gcj_support}
BuildArch:      noarch
%endif

BuildRequires:  java-rpmbuild >= 0:1.7.2
BuildRequires:  ant, ant-nodeps
BuildRequires:  junit 
%if %{with_maven}
BuildRequires:  maven2-common-poms
BuildRequires:  maven2
BuildRequires:  maven2-plugin-ant
#BuildRequires:  maven2-plugin-changelog
BuildRequires:  maven2-plugin-compiler
BuildRequires:  maven2-plugin-install
BuildRequires:  maven2-plugin-jar
BuildRequires:  maven2-plugin-javadoc
BuildRequires:  maven2-plugin-plugin
BuildRequires:  maven2-plugin-resources
BuildRequires:  maven2-plugin-site
BuildRequires:  maven2-plugin-surefire
%endif
BuildRequires:  classworlds
BuildRequires:  jakarta-commons-collections
BuildRequires:  jakarta-commons-lang
BuildRequires:  jakarta-oro
BuildRequires:  jmock
BuildRequires:  maven2
BuildRequires:  maven-doxia >= 0:1.0-0.a10
#BuildRequires:  maven-shared-plugin-testing-harness
#BuildRequires:  maven-shared-reporting-impl
BuildRequires:  plexus-container-default
BuildRequires:  plexus-i18n
BuildRequires:  plexus-utils
BuildRequires:  plexus-velocity
BuildRequires:  velocity

Requires:  classworlds
Requires:  jakarta-commons-collections
Requires:  jakarta-commons-lang
Requires:  jakarta-oro
#Requires:  maven-shared-reporting-impl
Requires:  plexus-container-default
Requires:  plexus-i18n
Requires:  plexus-utils
Requires:  plexus-velocity


Requires(post):    jpackage-utils >= 0:1.7.2
Requires(postun):  jpackage-utils >= 0:1.7.2

%if %{gcj_support}
BuildRequires:          java-gcj-compat-devel
%endif

%description
Maven JXR is a source cross referencing tool.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
Javadoc for %{name}.

%prep
%setup -q 
cp %{SOURCE1} build.xml
cp %{SOURCE3} settings.xml
gzip -dc %{SOURCE4} | tar xf -
sed -i -e "s|<url>__JPP_URL_PLACEHOLDER__</url>|<url>file://`pwd`/.m2/repository</url>|g" settings.xml
sed -i -e "s|<url>__JAVADIR_PLACEHOLDER__</url>|<url>file://`pwd`/external_repo</url>|g" settings.xml
sed -i -e "s|<url>__MAVENREPO_DIR_PLACEHOLDER__</url>|<url>file://`pwd`/.m2/repository</url>|g" settings.xml
%patch0 -b .sav0
%patch1 -b .sav1


%build

export JAVA_HOME=%{_jvmdir}/java-rpmbuild

export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mkdir -p $MAVEN_REPO_LOCAL

mkdir external_repo
ln -s %{_javadir} external_repo/JPP

export M2_SETTINGS=$(pwd)/settings.xml
%if %{with_maven}
mvn-jpp \
        -e \
        -s $M2_SETTINGS \
        -Dmaven2.jpp.depmap.file=%{SOURCE2} \
        -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        -Dmaven.test.failure.ignore=true \
        ant:ant install javadoc:javadoc
%else
#maven2/artifact \
#maven2/artifact-manager \
#maven2/core \
#maven2/model \
#maven2/plugin-api \
#maven2/plugin-descriptor \
#maven2/profile \
#maven2/project \
#maven2/settings \
#maven-wagon/provider-api \
#plexus/container-default \

export CLASSPATH=$(build-classpath \
classworlds \
commons-collections \
commons-lang \
maven2/artifact \
maven2/artifact-manager \
maven2/core \
maven2/model \
maven2/plugin-api \
maven2/project \
maven2/reporting-api \
maven-doxia/site-renderer \
maven-shared/plugin-testing-harness \
maven-shared/reporting-impl \
plexus/container-default \
plexus/utils \
oro \
velocity \
)
CLASSPATH=$CLASSPATH:target/classes:target/test-classes
pushd maven-jxr
   %{ant} -Dmaven.settings.offline=true -Dbuild.sysclasspath=only jar javadoc
popd

export CLASSPATH=$(build-classpath \
classworlds \
commons-collections \
commons-lang \
maven2/artifact \
maven2/artifact-manager \
maven2/core \
maven2/model \
maven2/monitor \
maven2/plugin-api \
maven2/plugin-descriptor \
maven2/plugin-parameter-documenter \
maven2/plugin-registry \
maven2/plugin-repository-metadata \
maven2/profile \
maven2/project \
maven2/reporting-api \
maven2/settings \
maven-doxia/core \
maven-doxia/sink-api \
maven-doxia/site-renderer \
maven-shared/plugin-testing-harness \
maven-shared/reporting-impl \
oro \
plexus/container-default \
plexus/i18n \
plexus/utils \
plexus/velocity \
velocity \
)
CLASSPATH=$CLASSPATH:$(pwd)/maven-jxr/target/maven-jxr-%{version}.jar
CLASSPATH=$CLASSPATH:target/classes:target/test-classes
pushd maven-jxr-plugin
mkdir -p target/classes/META-INF/maven/org.apache.maven.plugins/maven-jxr-plugin
cp pom.xml target/classes/META-INF/maven/org.apache.maven.plugins/maven-jxr-plugin
cat > target/classes/META-INF/maven/org.apache.maven.plugins/maven-jxr-plugin/pom.properties <<EOT
version=%{version}
groupId=org.apache.maven.plugins
artifactId=maven-jxr-plugin
EOT
   %{ant} -Dmaven.settings.offline=true -Dbuild.sysclasspath=only jar javadoc
popd
%endif

%install
rm -rf $RPM_BUILD_ROOT
# jars/poms
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/plugins

%add_to_maven_depmap org.apache.maven.jxr jxr %{version} JPP %{name}-parent
install -pm 644 pom.xml $RPM_BUILD_ROOT/%{_datadir}/maven2/poms/JPP-%{name}-parent.pom

install -m 644 %{name}/target/%{name}-%{version}.jar \
               $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
%add_to_maven_depmap org.apache.maven %{name} %{version} JPP %{name}
install -pm 644 %{name}/pom.xml $RPM_BUILD_ROOT/%{_datadir}/maven2/poms/JPP-%{name}.pom

(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)

install -m 644 %{name}-plugin/target/%{name}-plugin-%{version}.jar \
    $RPM_BUILD_ROOT%{_datadir}/maven2/plugins/jxr-plugin-%{version}.jar
%add_to_maven_depmap org.apache.maven.plugins %{name}-plugin %{version} JPP/maven2/plugins jxr-plugin
install -m 644 %{name}-plugin/pom.xml \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.maven2.plugins-jxr-plugin.pom
(cd $RPM_BUILD_ROOT%{_datadir}/maven2/plugins && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)


# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}/
cp -pr %{name}/target/site/apidocs/* \
                    $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}/
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}/plugin
cp -pr %{name}-plugin/target/site/apidocs/* \
                    $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}/plugin
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name} # ghost symlink

%{gcj_compile}

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
%{gcj_files}

%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/*
