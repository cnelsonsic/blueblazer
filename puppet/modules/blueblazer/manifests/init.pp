# == Class: blueblazer
#
# All the things required to fire up a blueblazer http server.
#
# === Examples
#
#  class { 'blueblazer': }
#
# === Authors
#
# Charles Nelson <cnelsonsic@gmail.com>
#
# === Copyright
#
# Copyright 2012 Charles Nelson, unless otherwise noted.
# This file is part of BlueBlazer
#
# BlueBlazer is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
class blueblazer {
  package { [
      'gunicorn',
      'git+git://github.com/cnelsonsic/blueblazer.git',
    ]:
    ensure   => 'latest',
    provider => 'pip',
  }

  package { [
    'supervisor',
    'nginx',
  ]:
    ensure   => 'latest',
  }

  service {'supervisor':
    ensure  => 'running',
    enable  => true,
    require => Package['supervisor'],
  }

  service {'nginx':
    ensure  => 'running',
    enable  => true,
    require => Package['nginx'],
  }

  file {['/var/www', '/var/www/blueblazer']:
    ensure => 'directory',
  }

  # If there's no checkout, check it out
  $blueblazer_git = 'git://github.com/cnelsonsic/blueblazer.git'
  exec {'git clone':
    path    => $::path,
    cwd     => '/var/www/blueblazer',
    onlyif  => 'test ! -f /var/www/blueblazer/setup.py',
    command => "git clone ${blueblazer_git} .",
    require => File['/var/www'],
    notify  => Service['supervisor'],
  }

  # If there's a checkout, make sure it's running the latest.
  exec {'refresh git':
    path    => $::path,
    cwd     => '/var/www/blueblazer',
    onlyif  => 'test -f /var/www/blueblazer/setup.py',
    command => 'git fetch origin; git checkout origin/master',
    require => Exec['git clone'],
    notify  => Service['supervisor'],
  }

  file { ['/etc/supervisor', '/etc/supervisor/conf.d', ]:
    ensure => 'directory',
  }
  file { '/etc/supervisor/conf.d/blueblazer.conf':
    content => template('blueblazer/blueblazer.conf'),
    require => File['/etc/supervisor/conf.d'],
    notify  => Service['supervisor'],
  }

  # Set up the includes for supervisord configs.
  augeas {'supervisord.conf':
    lens    => 'MySQL.lns',
    incl    => '/etc/supervisor/supervisord.conf',
    context => '/files/etc/supervisor/supervisord.conf/target[5]/',
    changes => 'set files /etc/supervisor/conf.d/*.conf',
    notify  => Service['supervisor'],
  }

  # Set up nginx configs.
  file { '/etc/nginx/locations/blueblazer.conf':
    content => template('blueblazer/blueblazer.nginx.conf'),
    require => File['/etc/nginx/locations'],
    notify  => Service['nginx'],
  }

  file { ['/etc/nginx/upstreams', '/etc/nginx/locations']:
    ensure  => 'directory',
    require => Package['nginx'],
  }
  file { '/etc/nginx/upstreams/blueblazer.conf':
    content => template('blueblazer/blueblazer.upstream.nginx.conf'),
    require => File['/etc/nginx/upstreams'],
    notify  => Service['nginx'],
  }
}
