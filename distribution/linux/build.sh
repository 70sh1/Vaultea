#!/bin/sh

pyinstaller --clean --noconfirm linux.spec

rm dist/vaultea/libstdc++.so.6

# Create folders.
[ -e package ] && rm -r package
mkdir -p package/opt
mkdir -p package/usr/bin
mkdir -p package/usr/share/applications
mkdir -p package/usr/share/icons/hicolor

# Copy files
cp -r dist/vaultea package/opt/vaultea
cp -r linux-icons/* package/usr/share/icons/hicolor
cp vaultea.desktop package/usr/share/applications

# Create usr/bin alias
echo #!/bin/sh >> package/usr/bin/vaultea
echo exec /opt/vaultea/vaultea >> package/usr/bin/vaultea

# Change permissions
find package/opt/vaultea -type f -exec chmod 644 -- {} +
find package/opt/vaultea -type d -exec chmod 755 -- {} +
find package/usr/share -type f -exec chmod 644 -- {} +
chmod +x package/opt/vaultea/vaultea
chmod +x package/usr/bin/vaultea


# Uses .fpm file
fpm --force --output-type deb
fpm --force --output-type rpm
fpm --force --output-type pacman

# Cleanup
rm -rf dist
rm -rf build
rm -rf package