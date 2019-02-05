%if 0%{?fedora}
  %bcond_without python3
  %bcond_without python2
%else
  %if 0%{?rhel} > 7
    %bcond_with    python2
    %bcond_without python3
  %else
    %bcond_without python2
    %bcond_with    python3
  %endif
%endif

%bcond_without check
%bcond_without debugrpms

%global srcname	psycopg2
%global sum	A PostgreSQL database adapter for Python
%global desc	Psycopg is the most popular PostgreSQL adapter for the Python \
programming language. At its core it fully implements the Python DB \
API 2.0 specifications. Several extensions allow access to many of the \
features offered by PostgreSQL.

%global python_runtimes	%{?with_python2:python2 %{?with_debugrpms:python2-debug}} \\\
                        %{?with_python3:python3 %{?with_debugrpms:python3-debug}}

%{!?with_python2:%{!?with_python3:%{error:one python version needed}}}

# Python 2.5+ is not supported by Zope, so it does not exist in
# recent Fedora releases. That's why zope subpackage is disabled.
%global zope 0
%if %zope
%global ZPsycopgDAdir %{_localstatedir}/lib/zope/Products/ZPsycopgDA
%endif


Summary:	%{sum}
Name:		python-%{srcname}
Version:	2.7.7
Release:	1%{?dist}
# The exceptions allow linking to OpenSSL and PostgreSQL's libpq
License:	LGPLv3+ with exceptions
Url:		http://www.psycopg.org/psycopg/

Source0:	http://www.psycopg.org/psycopg/tarballs/PSYCOPG-2-7/psycopg2-%{version}.tar.gz

%{?with_python2:BuildRequires:	%{?with_debugrpms:/usr/bin/python2-debug} python2-devel}
%{?with_python3:BuildRequires:	%{?with_debugrpms:/usr/bin/python3-debug} python3-devel}

BuildRequires:  gcc
BuildRequires: pkgconfig(libpq)

# For testsuite
%if %{with check}
BuildRequires:	postgresql-test-rpm-macros
%endif

Conflicts:	python-psycopg2-zope < %{version}

%description
%{desc}


%if %{with python2}
%package -n python2-%{srcname}
%{?python_provide:%python_provide python2-%{srcname}}
Summary: %{sum} 2

%description -n python2-%{srcname}
%{desc}


%package -n python2-%{srcname}-tests
Summary: A testsuite for %sum 2
Requires: python2-%srcname = %version-%release

%description -n python2-%{srcname}-tests
%desc
This sub-package delivers set of tests for the adapter.


%if %{with debugrpms}
%package -n python2-%{srcname}-debug
Summary: A PostgreSQL database adapter for Python 2 (debug build)
# Require the base package, as we're sharing .py/.pyc files:
Requires:	python2-%{srcname} = %{version}-%{release}
%{?python_provide:%python_provide python2-%{srcname}-debug}

%description -n python2-%{srcname}-debug
This is a build of the psycopg PostgreSQL database adapter for the debug
build of Python 2.
%endif # debugrpms
%endif # python2


%if %{with python3}
%package -n python3-psycopg2
Summary: %{sum} 3
%{?python_provide:%python_provide python3-%{srcname}}

%description  -n python3-psycopg2
%{desc}


%package -n python3-%{srcname}-tests
Summary: A testsuite for %sum 2
Requires: python3-%srcname = %version-%release

%description -n python3-%{srcname}-tests
%desc
This sub-package delivers set of tests for the adapter.


%if %{with debugrpms}
%package -n python3-psycopg2-debug
Summary: A PostgreSQL database adapter for Python 3 (debug build)
# Require base python 3 package, as we're sharing .py/.pyc files:
Requires:	python3-psycopg2 = %{version}-%{release}

%description -n python3-%{srcname}-debug
This is a build of the psycopg PostgreSQL database adapter for the debug
build of Python 3.
%endif # debugrpms
%endif # python3


%package doc
Summary:	Documentation for psycopg python PostgreSQL database adapter
%{?with_python2:Provides: python2-%{srcname}-doc = %{version}-%{release}}
%{?with_python3:Provides: python3-%{srcname}-doc = %{version}-%{release}}

%description doc
Documentation and example files for the psycopg python PostgreSQL
database adapter.


%if %zope
%package zope
Summary:	Zope Database Adapter ZPsycopgDA
# The exceptions allow linking to OpenSSL and PostgreSQL's libpq
License:	GPLv2+ with exceptions or ZPLv1.0
Requires:	%{name} = %{version}-%{release}
Requires:	zope

%description zope
Zope Database Adapter for PostgreSQL, called ZPsycopgDA
%endif


%prep
%autosetup -p1 -n psycopg2-%{version}


%build
export CFLAGS=${RPM_OPT_FLAGS} LDFLAGS=${RPM_LD_FLAGS}
for python in %{python_runtimes} ; do
  $python setup.py build
done

# Fix for wrong-file-end-of-line-encoding problem; upstream also must fix this.
for i in `find doc -iname "*.html"`; do sed -i 's/\r//' $i; done
for i in `find doc -iname "*.css"`; do sed -i 's/\r//' $i; done

# Get rid of a "hidden" file that rpmlint complains about
rm -f doc/html/.buildinfo

# We can not build docs now:
# https://www.postgresql.org/message-id/2741387.dvL6Cb0VMB@nb.usersys.redhat.com
# make -C doc/src html


%check
%if %{with check}
export PGTESTS_LOCALE=C.UTF-8
%postgresql_tests_run

export PSYCOPG2_TESTDB=${PGTESTS_DATABASES##*:}
export PSYCOPG2_TESTDB_HOST=$PGHOST
export PSYCOPG2_TESTDB_PORT=$PGPORT

cmd="from psycopg2 import tests; tests.unittest.main(defaultTest='tests.test_suite')"

%if %{with python2}
PYTHONPATH=%buildroot%python2_sitearch %__python2 -c "$cmd" --verbose
%endif
%if %{with python3}
PYTHONPATH=%buildroot%python3_sitearch %__python3 -c "$cmd" --verbose
%endif
%endif # check


%install
export CFLAGS=${RPM_OPT_FLAGS} LDFLAGS=${RPM_LD_FLAGS}
for python in %{python_runtimes} ; do
  $python setup.py install --no-compile --root %{buildroot}
done

%if %zope
install -d %{buildroot}%{ZPsycopgDAdir}
cp -pr ZPsycopgDA/* %{buildroot}%{ZPsycopgDAdir}
%endif

# This test is skipped on 3.7 and has a syntax error so brp-python-bytecompile would choke on it
%{?with_python3:rm -r %{buildroot}%{python3_sitearch}/%{srcname}/tests/test_async_keyword.py}

%if %{with python2}
%files -n python2-psycopg2
%license LICENSE
%doc AUTHORS NEWS README.rst
%dir %{python2_sitearch}/psycopg2
%{python2_sitearch}/psycopg2/*.py
%{python2_sitearch}/psycopg2/*.pyc
%{python2_sitearch}/psycopg2/_psycopg.so
%{python2_sitearch}/psycopg2/*.pyo
%{python2_sitearch}/psycopg2-%{version}-py2*.egg-info


%files -n python2-%{srcname}-tests
%{python2_sitearch}/psycopg2/tests


%if %{with debugrpms}
%files -n python2-%{srcname}-debug
%license LICENSE
%{python2_sitearch}/psycopg2/_psycopg_d.so
%endif # debugrpms
%endif # python2


%if %{with python3}
%files -n python3-psycopg2
%license LICENSE
%doc AUTHORS NEWS README.rst
%dir %{python3_sitearch}/psycopg2
%{python3_sitearch}/psycopg2/*.py
%{python3_sitearch}/psycopg2/_psycopg.cpython-3?m*.so
%dir %{python3_sitearch}/psycopg2/__pycache__
%{python3_sitearch}/psycopg2/__pycache__/*.py{c,o}
%{python3_sitearch}/psycopg2-%{version}-py3*.egg-info


%files -n python3-%{srcname}-tests
%{python3_sitearch}/psycopg2/tests


%if %{with debugrpms}
%files -n python3-psycopg2-debug
%license LICENSE
%{python3_sitearch}/psycopg2/_psycopg.cpython-3?dm*.so
%endif # debugrpms
%endif # python3


%files doc
%license LICENSE
%doc doc examples/


%if %zope
%files zope
%license LICENSE
%dir %{ZPsycopgDAdir}
%{ZPsycopgDAdir}/*.py
%{ZPsycopgDAdir}/*.pyo
%{ZPsycopgDAdir}/*.pyc
%{ZPsycopgDAdir}/dtml/*
%{ZPsycopgDAdir}/icons/*
%endif


%changelog
* Tue Feb 05 2019 Pavel Raiskup <praiskup@redhat.com> - 2.7.7-1
- update to the latest upstream release

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.5-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Oct 03 2018 Pavel Raiskup <praiskup@redhat.com> - 2.7.5-5
- prepare --without=debugrpms option (rhbz#1635166)
- get the python2 packages back for a while (rhbz#1634973)

* Wed Oct 03 2018 Pavel Raiskup <praiskup@redhat.com> - 2.7.5-4
- drop python2* on f30+ (rhbz#1634973)
- use proper compiler/linker flags (rhbz#1631713)
- correct the (build)requires

* Tue Jul 17 2018 Pavel Raiskup <praiskup@redhat.com> - 2.7.5-3
- standalone installable doc subpackage

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Jul 02 2018 Miro Hrončok <mhroncok@redhat.com> - 2.7.5-2
- Rebuilt for Python 3.7

* Mon Jun 18 2018 Pavel Raiskup <praiskup@redhat.com> - 2.7.5-1
- rebase to latest upstream release, per release notes:
  http://initd.org/psycopg/articles/2018/06/17/psycopg-275-released/

* Sat Jun 16 2018 Miro Hrončok <mhroncok@redhat.com> - 2.7.4-5
- Rebuilt for Python 3.7

* Mon May 21 2018 Pavel Raiskup <praiskup@redhat.com> - 2.7.4-4
- fix for python 3.7, by mhroncok

* Fri Apr 13 2018 Pavel Raiskup <praiskup@redhat.com> - 2.7.4-3
- depend on postgresql-test-rpm-macros

* Fri Apr 13 2018 Pavel Raiskup <praiskup@redhat.com> - 2.7.4-2
- re-enable testsuite

* Mon Feb 12 2018 Pavel Raiskup <praiskup@redhat.com> - 2.7.4-1
- rebase to latest upstream release, per release notes:
  http://initd.org/psycopg/articles/2018/02/08/psycopg-274-released/

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.3.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Dec 14 2017 Pavel Raiskup <praiskup@redhat.com> - 2.7.3.2-2
- treat python3/python2 equally

* Wed Oct 25 2017 Pavel Raiskup <praiskup@redhat.com> - 2.7.3.2-1
- update to 2.7.3.2, per release notes:
  http://initd.org/psycopg/articles/2017/10/24/psycopg-2732-released/

* Mon Aug 28 2017 Pavel Raiskup <praiskup@redhat.com> - 2.7.3.1-1
- http://initd.org/psycopg/articles/2017/08/26/psycopg-2731-released/

* Sun Aug 13 2017 Pavel Raiskup <praiskup@redhat.com> - 2.7.3-1
- rebase to latest upstream release, per release notes:
  http://initd.org/psycopg/articles/2017/07/24/psycopg-273-released/

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sun Jul 23 2017 Pavel Raiskup <praiskup@redhat.com> - 2.7.2-1
- rebase to latest upstream release, per release notes:
  http://initd.org/psycopg/articles/2017/07/22/psycopg-272-released/

* Mon Mar 13 2017 Pavel Raiskup <praiskup@redhat.com> - 2.7.1-1
- rebase to latest upstream release, per release notes:
  http://initd.org/psycopg/articles/2017/03/01/psycopg-271-released/
- fix testsuite

* Thu Mar 02 2017 Pavel Raiskup <praiskup@redhat.com> - 2.7-1
- rebase to latest upstream release, per release notes:
  http://initd.org/psycopg/articles/2017/03/01/psycopg-27-released/
- enable testsuite during build, and package it

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Dec 09 2016 Charalampos Stratakis <cstratak@redhat.com> - 2.6.2-3
- Rebuild for Python 3.6

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6.2-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Thu Jul 07 2016 Pavel Raiskup <praiskup@redhat.com> - 2.6.2-1
- rebase (rhbz#1353545), per release notes
  http://initd.org/psycopg/articles/2016/07/07/psycopg-262-released/

* Sun May 29 2016 Pavel Raiskup <praiskup@redhat.com> - 2.6.1-6
- provide python2-psycopg2 (rhbz#1306025)
- cleanup obsoleted packaging stuff

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sun Nov 15 2015 Pavel Raiskup <praiskup@redhat.com> - 2.6.1-4
- again bump for new Python 3.5, not build previously?
- fix rpmlint issues
- no pyo files with python 3.5

* Tue Nov 10 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Changes/python3.5

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.6.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 15 2015 Jozef Mlich <jmlich@redhat.com> 2.6.1-1
- Update to 2.6.1

* Mon Feb 9 2015 Devrim Gündüz <devrim@gunduz.org> 2.6-1
- Update to 2.6, per changes described at:
  http://www.psycopg.org/psycopg/articles/2015/02/09/psycopg-26-and-255-released/

* Tue Jan 13 2015 Devrim Gündüz <devrim@gunduz.org> 2.5.4-1
- Update to 2.5.4, per changes described at:
  http://www.psycopg.org/psycopg/articles/2014/08/30/psycopg-254-released

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Jul 04 2014 Pavel Raiskup <praiskup@redhat.com> - 2.5.3-1
- rebase to most recent upstream version, per release notes:
  http://www.psycopg.org/psycopg/articles/2014/05/13/psycopg-253-released/

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue May 13 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 2.5.2-2
- Rebuilt for https://fedoraproject.org/wiki/Changes/Python_3.4

* Tue Jan 7 2014 Devrim Gündüz <devrim@gunduz.org> 2.5.2-1
- Update to 2.5.2, per changes described at:
  http://www.psycopg.org/psycopg/articles/2014/01/07/psycopg-252-released

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sun Jul 07 2013 Pavel Raiskup <praiskup@redhat.com> - 2.5.1-1
- rebase to 2.5.1

* Thu May 16 2013 Devrim Gündüz <devrim@gunduz.org> 2.5-1
- Update to 2.5, per changes described at:
  http://www.psycopg.org/psycopg/articles/2013/04/07/psycopg-25-released/

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.5-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sat Aug 04 2012 David Malcolm <dmalcolm@redhat.com> - 2.4.5-6
- rebuild for https://fedoraproject.org/wiki/Features/Python_3.3

* Fri Aug  3 2012 David Malcolm <dmalcolm@redhat.com> - 2.4.5-5
- generalize python 3 fileglobbing to work with both Python 3.2 and 3.3

* Fri Aug  3 2012 David Malcolm <dmalcolm@redhat.com> - 2.4.5-4
- replace "python3.2dmu" with "python3-debug"; with_python3 fixes

* Fri Aug  3 2012 David Malcolm <dmalcolm@redhat.com> - 2.4.5-3
- add with_python3 conditional

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Apr  7 2012 Tom Lane <tgl@redhat.com> 2.4.5-1
- Update to 2.4.5

* Thu Feb  2 2012 Tom Lane <tgl@redhat.com> 2.4.4-1
- Update to 2.4.4
- More specfile neatnik-ism

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Nov 29 2011 Tom Lane <tgl@redhat.com> 2.4.2-2
- Fix mistaken %%dir marking on python3 files, per Dan Horak

* Sat Jun 18 2011 Tom Lane <tgl@redhat.com> 2.4.2-1
- Update to 2.4.2
Related: #711095
- Some neatnik specfile cleanups

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

* Sat Jul 22 2006 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.2-2
- Added dos2unix to buildrequires
- removed python related part from package name

* Fri Jul 21 2006 - Devrim GUNDUZ <devrim@commandprompt.com> 2.0.2-1
- Fix rpmlint errors, including dos2unix solution
- Re-engineered spec file

* Mon Jan 23 2006 - Devrim GUNDUZ <devrim@commandprompt.com>
- First 2.0.X build

* Mon Jan 23 2006 - Devrim GUNDUZ <devrim@commandprompt.com>
- Update to 1.2.21

* Tue Dec 06 2005 - Devrim GUNDUZ <devrim@commandprompt.com>
- Initial release for 1.1.20
