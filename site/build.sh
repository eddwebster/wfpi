#!/bin/sh
set -euo pipefail
MINIFY=node_modules/minify/bin/minify.js

npm i --no-optional minify@5.1.1

rm -fr dist
mkdir dist

cp -r img test dist

${MINIFY} index.html > dist/index.html
${MINIFY} style.css > dist/style.css
${MINIFY} test/index.html > dist/test/index.html
${MINIFY} test/assets/main.js > dist/test/assets/main.js
${MINIFY} test/assets/style.css > dist/test/assets/style.css

sed -i 's/vue\/dist\/vue\.js/vue\/dist\/vue\.min\.js/' dist/test/index.html
