boards
======

Lists all supported architectures

| Board                | Bootloader    | FPU          | GPU         | PRU     | FPGA           |
| -------------------- |  -----------  | ------------ | ----------- | ------- | -------------- |
| __beaglebone-black__ | uboot 2021.04 | SIMD &#9989; | SGX &#9989; | &#9989; |    x           |
| __116__              | uboot 2019.01 | SIMD &#9989; | SGX &#9989; | &#9989; |    x           |
| __microzed__         | uboot 2019.01 | SIMD &#9989; | SGX &#9989; | &#9989; | XLNX-7 &#9989; |

defining a board
================

+ board folder name cannot include whitespaces
+ $board/config : mandatory - minimum buildroot recipe fragment to build on this architecture.
It is mandatory to mark the cpu buildroot flag with a special `# cpu` comment in this file.
Refer to existing $board/config files.

+ $board/some-file.dts : optionnal and unique devicetree file
 + optionnal: in this case $board/config should name a standard inline devicetree file
 + when provided: must either be partial and to compile along standard inline devicetree files,
 or can be complete.

+ $board/xxxx-layer.dts: optionnal layers to be addded to main devicetre file.
Board will boot on the resulting configuration. This is described in image recipe.
Refer to exisintg recipes.

+ $board/xxx-overlay.dts: optionnal devicetree overlays, described in image recipe.
+ $board/linux-fragments: optionnal kernel fragments
+ $board/uboot-fragments: optionnal uboot fragments
