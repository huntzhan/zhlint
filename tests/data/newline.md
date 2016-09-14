以上代码来源于 [golang-redis-sample](https://github.com/DaoCloud/golang-redis-sample/blob/ship2.0.normal/daocloud.yml)，
该功能即我们常用的镜像构建功能，指定了三个参数：  
`dockerfile_path`：Dockerfile 相对代码根目录的路径，默认值为 `Dockerfile`  
`build_dir`：构建目录，`dockerfile_path` 必须在这个目录之下，默认是代码根目录，即 `/`  
`cache`：是否开启缓存，值为 `true`（开启）和 `false`（关闭）
