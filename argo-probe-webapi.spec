# sitelib
%define dir /usr/libexec/argo/probes/webapi
%global __python %{python3}

Name:          argo-probe-webapi
Summary:       Probe checking ARGO WEB-API component.
Version:       0.2.0
Release:       1%{?dist}
License:       ASL 2.0
Source0:       %{name}-%{version}.tar.gz
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root
Group:         Network/Monitoring
BuildArch:     noarch
BuildRequires: python3-devel

%if 0%{?el7}
Requires:      python36-requests

%else
Requires:      python3-requests

%endif


%description
This package includes probe that checks ARGO WEB-API.

%prep
%setup -q

%build
%{py3_build}

%install
%{py3_install "--record=INSTALLED_FILES"}

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%defattr(-,root,root,-)
%{python3_sitelib}/argo_probe_webapi
%{dir}


%changelog
* Thu Mar 7 2024 Katarina Zailac <kzailac@srce.hr> - 0.2.0-1%{?dist}
- ARGO-4477 Improve message when using single tenant
- ARGO-4478 Bug when having problems with status report
- ARGO-4474 Add performance data to argo-probe-webapi
- ARGO-4443 Refactor of argo-probe-webapi report print
* Fri Jun 10 2022 Katarina Zailac <kzailac@gmail.com> - 0.1.0-1%{?dist}
- AO-650 Harmonize argo-mon probes
