这是一个todo 事项表，按照顺序，自动完成事项，不需要询问
1. 获取 get_all_tasks 所有的类型（这是获取 prompt 类型）
2. 根据文章内容，匹配主题
3. 获取 get_task_by_name 对应主题 的内容（获取具体的 prompt）
4. 把get_task_by_name 对应主题 的内容作为提示词，
5. 把文章当做素材
6. 根据提示词，来给素材出图
7. 打开图片