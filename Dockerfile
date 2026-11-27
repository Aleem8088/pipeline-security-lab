# Pinned by digest (the tag is a movable label, like an action tag). Dependabot keeps it current.
FROM node:24-alpine@sha256:116b800c3754b440ee0aa3ed2f20f5bf3d99a554bfd9adeea09ea8017f6e85f5
WORKDIR /app
COPY package*.json ./
# Install the app's dependencies, then delete npm and yarn from the final image: the running
# service does not need a package manager, and the scanner found most remaining issues in them.
RUN npm ci --omit=dev && npm cache clean --force \
 && rm -rf /usr/local/lib/node_modules /usr/local/bin/npm /usr/local/bin/npx \
           /opt/yarn-* /usr/local/bin/yarn /usr/local/bin/yarnpkg
COPY src ./src
USER node
EXPOSE 3000
CMD ["node", "src/server.js"]
