import { useState, useEffect } from 'react'
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  message,
  Space,
  Tag as AntTag,
  ColorPicker,
  Typography,
} from 'antd'
import {
  EditOutlined,
  TagsOutlined,
} from '@ant-design/icons'
import { tagService } from '../../services'
import type { Tag, TagUpdate } from '../../types'
import { formatDate } from '../../utils/format'
import type { ColumnsType } from 'antd/es/table'

const { Title } = Typography

export default function TagManagement() {
  const [tags, setTags] = useState<Tag[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingTag, setEditingTag] = useState<Tag | null>(null)
  const [form] = Form.useForm()

  useEffect(() => {
    fetchTags()
  }, [])

  const fetchTags = async () => {
    setLoading(true)
    try {
      const data = await tagService.getTags()
      setTags(data)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取标签失败')
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = (record: Tag) => {
    setEditingTag(record)
    form.setFieldsValue({
      name: record.name,
      color: record.color || '#1890ff',
    })
    setModalVisible(true)
  }

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()

      const data = {
        name: values.name,
        color: typeof values.color === 'string' ? values.color : values.color?.toHexString?.(),
      }

      if (editingTag) {
        await tagService.updateTag(editingTag.id, data as TagUpdate)
        message.success('更新成功')
      } 
      // Removed create logic

      setModalVisible(false)
      form.resetFields()
      fetchTags()
    } catch (error: any) {
      if (error.errorFields) {
        return
      }
      message.error(error.response?.data?.detail || '操作失败')
    }
  }

  const columns: ColumnsType<Tag> = [
    {
      title: '标签名称',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: Tag) => (
        <AntTag color={record.color || 'blue'}>{name}</AntTag>
      ),
    },
    {
      title: '颜色',
      dataIndex: 'color',
      key: 'color',
      render: (color: string) => (
        <div
          style={{
            width: 60,
            height: 30,
            background: color || '#1890ff',
            borderRadius: 4,
            border: '1px solid #d9d9d9',
          }}
        />
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => formatDate(date),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <Card
        title={
          <Space>
            <TagsOutlined />
            <Title level={4} style={{ margin: 0 }}>标签管理</Title>
          </Space>
        }
        // Remove Add button
      >
        <Table
          columns={columns}
          dataSource={tags}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title='编辑标签'
        open={modalVisible}
        onOk={handleSubmit}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
        }}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="标签名称"
          >
            <Input disabled /> 
          </Form.Item>

          <Form.Item name="color" label="颜色">
            <ColorPicker showText />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}