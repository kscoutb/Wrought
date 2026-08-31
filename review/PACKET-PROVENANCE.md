# Review packet provenance

The packet sent to the external panel is **not** committed here. The courier repo is public; the
foundry source stays in the private repo and is referenced by commit and content hash instead.

- **Tag:** `review-rc2`
- **Tag object:** `fbb6782bf31df3df73f97b72bd917e70ce917c49`
- **Commit archived:** `bbecf2d41e074141c4cf7c9ad9e12ae42fb5e292`
- **Built with:** `git archive bbecf2d -- <paths>` — from the tag, never the working tree.

`MANIFEST.sha256` carries a SHA-256 for every file in the packet. To reconstruct it byte-for-byte,
`git archive` the same paths from `bbecf2d` and re-hash.

## One file is not from the tagged commit

`source/authproxy3.py` (`d3e1477a65b5755e7d9bdfad8e58b896015131803a1a70e4fc447c87b3f4e732`) is
**absent from `bbecf2d`**. It was taken from this repo at
`bundles/GATE-J0B-CLOSE/sources/authproxy3.py`, because §3 of `code-review.md` carries six findings
against it that the panel could not otherwise check. It is the only packet file outside the tag's
reproducibility guarantee, and it is already public here.

## The mandated §5.1 secret scan

    sudo -n /home/kalib/review-rc1/bin/wrought-precommit-secret-scan \
      --repo /home/kalib/review-rc1 --tree <packet>

    scanned 3 secret(s) from /etc/credstore.encrypted
    PASS  0 occurrences of any sealed credential in the scanned material
    exit 0

Three secrets, not two: `openrouter-review-key` was sealed into the credstore before the scan ran,
so the scan covers the very key this gate uses. An unsealed key would have been invisible to the
check that gates the egress.
