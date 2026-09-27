#!/usr/bin/env bash
# Builds the site and copies it into the folder of your PUBLIC website
# repository, ready to commit and push (GitHub Desktop, or git on the terminal).
# One-time: set SITE_REPO to the folder where that repository is cloned.
SITE_REPO="$HOME/ai-for-architecture"

cd "$(dirname "$0")"
if [ ! -d "$SITE_REPO/.git" ]; then
  echo
  echo "  $SITE_REPO is not a cloned repository."
  echo "  Edit the SITE_REPO line at the top of publish-site.sh so it points at"
  echo "  the folder where your website repository is cloned."
  exit 1
fi

echo; echo "  Step 1 of 2 - building the site"; echo "  -------------------------------"
python3 engine/build.py || { echo "  BUILD FAILED - read the message above."; exit 1; }

echo; echo "  Step 2 of 2 - copying site/ into $SITE_REPO"; echo "  --------------------------------------------"
if command -v rsync >/dev/null; then
  rsync -a --delete --exclude .git --exclude CNAME site/ "$SITE_REPO/"
else
  find "$SITE_REPO" -mindepth 1 -maxdepth 1 ! -name .git ! -name CNAME -exec rm -rf {} +
  cp -R site/. "$SITE_REPO/"
fi

echo
echo "  =========================================================="
echo "   Done. Now commit and push in that repository:"
echo "     cd \"$SITE_REPO\" && git add -A && git commit -m \"Update site\" && git push"
echo "   (or Commit + Push origin in GitHub Desktop). A minute later the site is updated."
echo "  =========================================================="
