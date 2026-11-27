# Pinned by digest (the tag is a movable label, like an action tag). Dependabot keeps it current.
FROM node:26-alpine@sha256:6bd9ab43c0ec0190ca7b2d193906cb8b7edf6e7f4afa43ddeccd6452710bffb5
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
