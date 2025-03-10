FROM centos:7

RUN cat <<'EOF' > /etc/yum.repos.d/CentOS-Base.repo
name=CentOS-$releasever - Base' >> /etc/yum.repos.d/CentOS-Base.repo && \
baseurl=http://vault.centos.org/7.9.2009/os/$basearch/' >> /etc/yum.repos.d/CentOS-Base.repo && \
gpgcheck=1' >> /etc/yum.repos.d/CentOS-Base.repo &&
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7' >> /etc/yum.repos.d/CentOS-Base.repo && \
>> /etc/yum.repos.d/CentOS-Base.repo && \
[updates]' >> /etc/yum.repos.d/CentOS-Base.repo && \
name=CentOS-$releasever - Updates' >> /etc/yum.repos.d/CentOS-Base.repo && \
baseurl=http://vault.centos.org/7.9.2009/updates/$basearch/' >> /etc/yum.repos.d/CentOS-Base.repo && \
gpgcheck=1' >> /etc/yum.repos.d/CentOS-Base.repo && \
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7' >> /etc/yum.repos.d/CentOS-Base.repo && \
>> /etc/yum.repos.d/CentOS-Base.repo && \
[extras]' >> /etc/yum.repos.d/CentOS-Base.repo && \
name=CentOS-$releasever - Extras' >> /etc/yum.repos.d/CentOS-Base.repo && \
baseurl=http://vault.centos.org/7.9.2009/extras/$basearch/' >> /etc/yum.repos.d/CentOS-Base.repo && \
gpgcheck=1' >> /etc/yum.repos.d/CentOS-Base.repo && \
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7' >> /etc/yum.repos.d/CentOS-Base.repo && \
EOF

RUN echo '[base]' > /etc/yum.repos.d/CentOS-Base.repo && \
	echo 'name=CentOS-$releasever - Base' >> /etc/yum.repos.d/CentOS-Base.repo && \
	echo 'baseurl=http://vault.centos.org/7.9.2009/os/$basearch/' \
		>> /etc/yum.repos.d/CentOS-Base.repo && \
	echo 'gpgcheck=1' >> /etc/yum.repos.d/CentOS-Base.repo && \
	echo 'gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7' \
		>> /etc/yum.repos.d/CentOS-Base.repo && \
	echo '' >> /etc/yum.repos.d/CentOS-Base.repo && \
	echo '[updates]' >> /etc/yum.repos.d/CentOS-Base.repo && \
	echo 'name=CentOS-$releasever - Updates' >> /etc/yum.repos.d/CentOS-Base.repo && \
	echo 'baseurl=http://vault.centos.org/7.9.2009/updates/$basearch/' \
		>> /etc/yum.repos.d/CentOS-Base.repo && \
	echo 'gpgcheck=1' >> /etc/yum.repos.d/CentOS-Base.repo && \
	echo 'gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7' \
		>> /etc/yum.repos.d/CentOS-Base.repo && \
	echo '' >> /etc/yum.repos.d/CentOS-Base.repo && \
	echo '[extras]' >> /etc/yum.repos.d/CentOS-Base.repo && \
	echo 'name=CentOS-$releasever - Extras' >> /etc/yum.repos.d/CentOS-Base.repo && \
	echo 'baseurl=http://vault.centos.org/7.9.2009/extras/$basearch/' \
		>> /etc/yum.repos.d/CentOS-Base.repo && \
	echo 'gpgcheck=1' >> /etc/yum.repos.d/CentOS-Base.repo && \
	echo 'gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7' \
		>> /etc/yum.repos.d/CentOS-Base.repo && \
	yum --assumeyes install python3
