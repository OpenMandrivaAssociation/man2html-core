%define posttag g
%define debian_release 6

Name:       man2html
Version:    1.6
Release:    3
Summary:    Convert man pages to HTML - CGI scripts
Group:      System/Base

# man2html.c and debian/sources/man2html.cgi.c are Copyright Only
# utils.c is GPL+
# everything else is GPLv2
License:    GPLv2+ and GPL+ and Copyright only

URL:        http://www.kapiti.co.nz/michael/vhman2html.html
Source0:    http://primates.ximian.com/~flucifredi/man/man-%{version}%{posttag}.tar.gz

# Debian CGI scripts
Source1:    http://ftp.de.debian.org/debian/pool/main/m/man2html/man2html_%{version}%{posttag}-%{debian_release}.debian.tar.gz

# Apache configuration file
Source2:    man2html.conf

# Patch1XXX are from Debian, XXX matches their patch number
# Copyright (C) Christoph Lameter <clameter@debian.org>, Nicolás Lichtmaier
# <nick@feedback.net.ar>, and Robert Luberda <robert@debian.org>.  GPLv2+

# fix a bashism in %%{_bindir}/hman, allows it to work on other shells
Patch1001:  man2html-hman-bashism.patch

# use relative links instead of http://localhost/
Patch1002:  man2html-relative-links.patch

# use file:/// links instead of file:/ (per RFC 1738)
Patch1013:  man2html-file-link.patch

# show hman(1) in man2html(1) see also section
Patch1017:  man2html-see-also-hman.patch

# *roff parser fix:  add support for \(lq and \(rq escape sequences
Patch1018:  man2html-quotes.patch

# fix SEGFAULT on manpages with no sections
Patch1019:  man2html-noindex-segfault.patch

# *roff parser fix: convert \N'123' to &#123
Patch1020:  man2html-escape-N.patch

# support Perl manpages (1p/3p/etc.)
Patch1021:  man2html-perl.patch

# fix typo in Italian man page
Patch1022:  man2html-it-typo.patch

# *roff parser: properly decode quotes inside quoted text
Patch1023:  man2html-double-quotes.patch

# *roff parser: handle \$* and \$@ escapes.
Patch1025:  man2html-all-args.patch

# *roff parser: support macro names longer than two characters
Patch1026:  man2html-macro-longnames.patch

# *roff parser: parse user defined macros before define ones
Patch1027:  man2html-macro-priority.patch

# fix a segfault that only happens on groff(1) [lol]
Patch1028:  man2html-groff-segfault.patch

# *roff parser:  support "\[xx]"
Patch1029:  man2html-new-macros.patch

# ignore font change requests that aren't followed by any words
Patch1031:  man2html-BR-empty-line.patch

# fix some GCC warnings
Patch1033:  man2html-gcc-warnings.patch

# Fedora patches

# use /usr/lib/man2html for CGI
# originally based on Debian patches 000 and 005
Patch1:  man2html-paths.patch

# support gunzipping manpages
# modified version of Debian patch 024
Patch2:  man2html-ungzip.patch
Patch3:  man2html-ungzip-makefile.patch

# fix up CGI scripts/Makefile with Fedora paths
Patch4:  man2html-cgi.patch

# hman cleanup: use xdg-open instead of lynxcgi by default and use correct path
#               for lynxcgi when manually requested
Patch5:  man2html-hman.patch

# manpage cleanup:  mention Fedora paths as default, use modern browser examples,
#                   and describe LYNXCGI issues as runtime, not compile-time
Patch6:  man2html-doc.patch

# fix format string warnings
# will send back to Debian as soon as I locate the part of my brain that
# remembers how to use their bugtracker
Patch7:  man2html-format.patch

# fix a bug in hman that linked to the wrong URL for mansec and manwhatis
# (e.g. when just invoking `hman 1`)
Patch8:  man2html-hman-section.patch

# fix the paths in localized manpages
Patch9:  man2html-localized-manpage-paths.patch

BuildRequires:  recode

Requires:   %{name}-core = %{version}-%{release}

%description
man2html is a man page to HTML converter.

This package contains CGI scripts that allow you to view, browse, and search
man pages using a web server.


%package core
Summary:  Convert man pages to HTML

%description core
man2html is a man page to HTML converter.

This package contains the man2html executable.


%prep
%setup -q -n man-%{version}%{posttag} -a1

for p in %{patches}; do
    patch -p1 -i $p
done


%build
CFLAGS="${CFLAGS:-%optflags}" ; export CFLAGS ;

# Configure and make man2html binary
#  (not autoconf so don't use %%configure)
./configure -d +fhs
%make

# make cgi scripts from debian
cd debian/sources
%make

%install
#install man2html binary
make -C man2html DESTDIR=%{buildroot} install install-hman

#install CGI scripts
make -C debian/sources PREFIX=%{buildroot} install

#install localized manpages
install -Dpm0644 man2html/locales/fr/man2html.1 %{buildroot}%{_mandir}/fr/man1/man2html.1
install -Dpm0644 man2html/locales/it/man2html.1 %{buildroot}%{_mandir}/it/man1/man2html.1
install -Dpm0644 man2html/locales/it/hman.1 %{buildroot}%{_mandir}/it/man1/hman.1

#convert localized manpages to UTF-8
recode latin1..utf8 \
    %{buildroot}%{_mandir}/fr/man1/man2html.1 \
    %{buildroot}%{_mandir}/it/man1/man2html.1 \
    %{buildroot}%{_mandir}/it/man1/hman.1 

#install httpd configuration
install -Dpm0644 %SOURCE2 %{buildroot}%{_sysconfdir}/httpd/conf.d/man2html.conf

#create cache directory for cgi scripts
mkdir -p %{buildroot}%{_localstatedir}/cache/man2html


%post
#clear out the cache directory so all future pages are regenerated with the new build
rm -f %{_localstatedir}/cache/man2html/* || :

%files
%attr(0755,-,-) %{_bindir}/hman
%{_prefix}/lib/man2html/
%attr(0775,root,apache) %{_localstatedir}/cache/man2html
%config(noreplace) %{_sysconfdir}/httpd/conf.d/man2html.conf
%{_mandir}/man1/hman.1.*


%files core
%{_bindir}/man2html
%{_mandir}/man1/man2html.1.*
%{_mandir}/*/man1/*.1.*
%doc COPYING HISTORY man2html/README man2html/TODO
