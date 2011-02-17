%global python_runtimes  python python-debug python3 python3.2dmu
# FIXME "python3.2dmu" should just be "python3-debug"

# Python major version.
%{expand: %%define pyver %(python -c 'import sys;print(sys.version[0:3])')}
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%{expand: %%define py3ver %(python3 -c 'import sys;print(sys.version[0:3])')}


# Python 2.5+ is not supported by Zope, so it does not exist in
# recent Fedora releases. That's why zope subpackage is disabled.
%global zope 0
%if %zope
%global ZPsycopgDAdir %{_localstatedir}/lib/zope/Products/ZPsycopgDA
%endif


Summary:	A PostgreSQL database adapter for Python
Name:		python-psycopg2
Version:	2.4
%global alphatag beta2
Release:	0.%{alphatag}%{?dist}
Source0:	http://initd.org/pub/software/psycopg/psycopg2-%{version}-%{alphatag}.tar.gz
# The exceptions allow linking to OpenSSL and PostgreSQL's libpq
License:	LGPLv3+ with exceptions
Group:		Applications/Databases
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Url:		http://www.initd.org/software/initd/psycopg

BuildRequires:	postgresql-devel
BuildRequires:	python-devel
BuildRequires:	python-debug
BuildRequires:	python3-devel
BuildRequires:	python3-debug

Conflicts:	python-psycopg2-zope < %{version}

%description
psycopg is a PostgreSQL database adapter for the Python programming
language (just like pygresql and popy.) It was written from scratch 
with the aim of being very small and fast, and stable as a rock. The 
main advantages of psycopg are that it supports the full Python
DBAPI-2.0 and being thread safe at level 2.

This is the first release of the new 2.2 series, supporting not just
one but two different ways of executing asynchronous queries, thanks to
Jan and Daniele (with a little help from me and others, but they did
99% of the work so they deserve their names here in the news.)

psycopg now supports both classic select() loops and "green" coroutine
libraries. It is all in the documentation, so just point your browser to
doc/html/advanced.html.

%package debug
Summary: A PostgreSQL database adapter for Python 2 (debug build)
# Require the base package, as we're sharing .py/.pyc files:
Requires: %{name}

%description debug
This is a build of the psycopg PostgreSQL database adapter for the debug
build of Python 2

%package -n python3-psycopg2
Summary: A PostgreSQL database adapter for Python 3

%description  -n python3-psycopg2
This is a build of the psycopg PostgreSQL database adapter for the Python 3

%package -n python3-psycopg2-debug
Summary: A PostgreSQL database adapter for Python 3 (debug build)

# Require base python 3 package, as we're sharing .py/.pyc files:
Requires: python3-psycopg2

%description -n python3-psycopg2-debug
This is a build of the psycopg PostgreSQL database adapter for the debug
build of Python 3

%package doc
Summary:	Documentation for psycopg python PostgreSQL database adapter
Group:		Documentation
Requires:	%{name} = %{version}-%{release}

%description doc
Documentation and example files for the psycopg python PostgreSQL
database adapter.

%if %zope
%package zope
Summary:	Zope Database Adapter ZPsycopgDA
# The exceptions allow linking to OpenSSL and PostgreSQL's libpq
License:	GPLv2+ with exceptions or ZPLv1.0
Group:		Applications/Databases
Requires:	%{name} = %{version}-%{release} zope

%description zope
Zope Database Adapter for PostgreSQL, called ZPsycopgDA
%endif

%prep
%setup -q -n psycopg2-%{version}-%{alphatag}

%build
for python in %{python_runtimes} ; do
  $python setup.py build
done

# Fix for wrong-file-end-of-line-encoding problem; upstream also must fix this.
for i in `find doc -iname "*.html"`; do sed -i 's/\r//' $i; done
for i in `find doc -iname "*.css"`; do sed -i 's/\r//' $i; done

# Get rid of a "hidden" file that rpmlint complains about
rm -f doc/html/.buildinfo

%install

DoInstall() {
  PythonBinary=$1

  Python_SiteArch=$($PythonBinary -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")

  mkdir -p %{buildroot}$Python_SiteArch/psycopg2
  $PythonBinary setup.py install --no-compile --root %{buildroot}

  # We're not currently interested in packaging the test suite.
  rm -rf %{buildroot}$Python_SiteArch/psycopg2/tests
}

rm -rf %{buildroot}
for python in %{python_runtimes} ; do
  DoInstall $python
done

%if %zope
install -d %{buildroot}%{ZPsycopgDAdir}
cp -pr ZPsycopgDA/* %{buildroot}%{ZPsycopgDAdir}
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog INSTALL LICENSE README
%dir %{python_sitearch}/psycopg2
%{python_sitearch}/psycopg2/*.py
%{python_sitearch}/psycopg2/*.pyc
%{python_sitearch}/psycopg2/_psycopg.so
%{python_sitearch}/psycopg2/*.pyo
%{python_sitearch}/psycopg2-%{version}_%{alphatag}-py%{pyver}.egg-info

%files debug
%defattr(-,root,root)
%doc LICENSE
%{python_sitearch}/psycopg2/_psycopg_d.so

%files -n python3-psycopg2
%defattr(-,root,root)
%doc AUTHORS ChangeLog INSTALL LICENSE README
%dir %{python3_sitearch}/psycopg2
%{python3_sitearch}/psycopg2/*.py
%{python3_sitearch}/psycopg2/_psycopg.cpython-3?mu.so
%dir %{python3_sitearch}/psycopg2/__pycache__
%dir %{python3_sitearch}/psycopg2/__pycache__/*.pyc
%dir %{python3_sitearch}/psycopg2/__pycache__/*.pyo
%{python3_sitearch}/psycopg2-%{version}_%{alphatag}-py%{py3ver}.egg-info

%files -n python3-psycopg2-debug
%defattr(-,root,root)
%doc LICENSE
%{python3_sitearch}/psycopg2/_psycopg.cpython-3?dmu.so


%files doc
%defattr(-,root,root)
%doc doc examples/

%if %zope
%files zope
%defattr(-,root,root)
%dir %{ZPsycopgDAdir}
%{ZPsycopgDAdir}/*.py
%{ZPsycopgDAdir}/*.pyo
%{ZPsycopgDAdir}/*.pyc
%{ZPsycopgDAdir}/dtml/*
%{ZPsycopgDAdir}/icons/*
%endif

%changelog
* Thu Feb 10 2011 David Malcolm <dmalcolm@redhat.com> - 2.4-0.beta2
- 2.4.0-beta2
- add python 2 debug, python3 (optimized) and python3-debug subpackages

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.3.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Dec 29 2010 Tom Lane <tgl@redhat.com> 2.3.2-1
- Update to 2.3.2
- Clean up a few rpmlint warnings

* Fri Dec 03 2010 Jason L Tibbitts III <tibbs@math.uh.edu> - 2.2.2-3
- Fix incorrect (and invalid) License: tag.

* Thu Jul 22 2010 David Malcolm <dmalcolm@redhat.com> - 2.2.2-2
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Tue Jul 20 2010 Devrim GUNDUZ <devrim@gunduz.org> - 2.2.2-1
- Update to 2.2.2

* Tue May 18 2010 Devrim GUNDUZ <devrim@gunduz.org> - 2.2.1-1
- Update to 2.2.1
- Improve description for 2.2 features.
- Changelog for 2.2.0 is: 
   http://initd.org/pub/software/psycopg/ChangeLog-2.2

* Wed Mar 17 2010 Devrim GUNDUZ <devrim@gunduz.org> - 2.0.14-1
- Update to 2.0.14
- Update license (upstream switched to LGPL3)

* Sun Jan 24 2010 Tom Lane <tgl@redhat.com> 2.0.13-2
- Fix rpmlint complaints: remove unneeded explicit Requires:, use Conflicts:
  instead of bogus Obsoletes: to indicate lack of zope subpackage

* Sun Oct 18 2009 Devrim GUNDUZ <devrim@gunduz.org> - 2.0.13-1
- Update to 2.0.13

* Fri Aug 14 2009 Devrim GUNDUZ <devrim@gunduz.org> - 2.0.12-1
- Update to 2.0.12

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue May 19 2009 Devrim GUNDUZ <devrim@gunduz.org> - 2.0.11-1
- Update to 2.0.11

* Tue Apr 21 2009 Devrim GUNDUZ <devrim@gunduz.org> - 2.0.10-1
- Update to 2.0.10

* Fri Mar 20 2009 Devrim GUNDUZ <devrim@gunduz.org> - 2.0.9-1
- Update to 2.0.9

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Dec 04 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 2.0.8-2
- Rebuild for Python 2.6

* Sat Nov 29 2008 Devrim GUNDUZ <devrim@gunduz.org> - 2.0.8-1
- Update to 2.0.8

* Sat Nov 29 2008 Devrim GUNDUZ <devrim@gunduz.org> - 2.0.8-1
- Update to 2.0.8

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 2.0.7-3
- Rebuild for Python 2.6

* Thu May 29 2008 Todd Zullinger <tmz@pobox.com> - 2.0.7-2
- fix license tags

* Wed Apr 30 2008 Devrim GUNDUZ <devrim@commandprompt.com> 2.0.7-1
- Update to 2.0.7

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 2.0.6-4.1
- Autorebuild for GCC 4.3

* Mon Jan 21 2008 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.6-3.1
- Rebuilt against PostgreSQL 8.3

* Thu Jan 3 2008 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.6-3
- Rebuild for rawhide changes

* Tue Aug 28 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 2.0.6-2
- Rebuild for selinux ppc32 issue.

* Fri Jun 15 2007 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.6-1
- Update to 2.0.6

* Thu Apr 26 2007 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.5.1-8
- Disabled zope package temporarily.

* Wed Dec 6 2006 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.5.1-7
- Rebuilt

* Wed Dec 6 2006 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.5.1-5
- Bumped up spec version

* Wed Dec 6 2006 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.5.1-4
- Rebuilt for PostgreSQL 8.2.0

* Mon Sep 11 2006 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.5.1-3
- Rebuilt

* Wed Sep 6 2006 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.5.1-2
- Remove ghost'ing, per Python Packaging Guidelines

* Mon Sep 4 2006 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.5.1-1
- Update to 2.0.5.1

* Sun Aug 6 2006 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.3-3
- Fixed zope package dependencies and macro definition, per bugzilla review (#199784)
- Fixed zope package directory ownership, per bugzilla review (#199784)
- Fixed cp usage for zope subpackage, per bugzilla review (#199784)

* Mon Jul 31 2006 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.3-2
- Fixed 64 bit builds
- Fixed license
- Added Zope subpackage
- Fixed typo in doc description
- Added macro for zope subpackage dir

* Mon Jul 31 2006 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.3-1
- Update to 2.0.3
- Fixed spec file, per bugzilla review (#199784)

* Sat Jul 22 2006 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.2-3
- Removed python dependency, per bugzilla review. (#199784)
- Changed doc package group, per bugzilla review. (#199784)
- Replaced dos2unix with sed, per guidelines and bugzilla review (#199784)
- Fix changelog dates

* Sat Jul 21 2006 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.2-2
- Added dos2unix to buildrequires
- removed python related part from package name

* Fri Jul 20 2006 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.2-1
- Fix rpmlint errors, including dos2unix solution
- Re-engineered spec file

* Fri Jan 23 2006 - Devrim GUNDUZ <devrim@commandprompt.com>
- First 2.0.X build

* Fri Jan 23 2006 - Devrim GUNDUZ <devrim@commandprompt.com>
- Update to 1.2.21

* Tue Dec 06 2005 - Devrim GUNDUZ <devrim@commandprompt.com>
- Initial release for 1.1.20
