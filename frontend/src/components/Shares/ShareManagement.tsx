import { useState, useEffect } from 'react'
import {
  Card,
  Table,
  Button,
  Switch,
  message,
  Space,
  Tag,
  Popconfirm,
  Typography,
  Tooltip,
} from 'antd'
import {
  ShareAltOutlined,
  CopyOutlined,
  DeleteOutlined,
  LockOutlined,
  UnlockOutlined,
} from '@ant-design/icons'
import { shareService } from '../../services'
import type { Share } from '../../types'
import { formatDate, copyToClipboard } from '../../utils/format'
import type { ColumnsType } from 'antd/es/table'

const { Title } = Typography

export default function ShareManagement() {
  const [shares, setShares] = useState<Share[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchShares()
  }, [])

  const fetchShares = async () => {
    setLoading(true)
    try {
      const data = await shareService.getShares()
      setShares(data)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取分享链接失败')
    } finally {
      setLoading(false)
    }
  }

  const handleCopyLink = (token: string) => {
    const link = `${window.location.origin}/share/${token}`
    copyToClipboard(link).then((success) => {
      if (success) {
        message.success('链接已复制到剪贴板')
      } else {
        message.error('复制失败,请手动复制')
      }
    })
  }

  const handleDelete = async (id: number) => {
    try {
      await shareService.deleteShare(id)
      message.success('删除成功')
      fetchShares()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败')
    }
  }

  const handleToggleActive = async (id: number, isActive: boolean) => {
    try {
      await shareService.updateShare(id, { is_active: !isActive })
      message.success(isActive ? '已停用' : '已激活')
      fetchShares()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '更新失败')
    }
  }

  const columns: ColumnsType<Share> = [
    {
      title: '对话 ID',
      dataIndex: 'conversation_id',
      key: 'conversation_id',
    },
    {
      title: '分享链接',
      dataIndex: 'share_token',
      key: 'share_token',
      render: (token: string) => (
        <Space>
          <Typography.Text code copyable={{ text: `${window.location.origin}/share/${token}` }}>
            {token.substring(0, 8)}...
          </Typography.Text>
          <Tooltip title="复制完整链接">
            <Button
              type="text"
              size="small"
              icon={<CopyOutlined />}
              onClick={() => handleCopyLink(token)}
            />
          </Tooltip>
        </Space>
      ),
    },
    {
      title: '保护',
      dataIndex: 'password',
      key: 'password',
      render: (password: string) =>
        password ? (
          <Tag icon={<LockOutlined />} color="orange">
            密码保护
          </Tag>
        ) : (
          <Tag icon={<UnlockOutlined />} color="green">
            公开
          </Tag>
        ),
    },
    {
      title: '访问次数',
      dataIndex: 'access_count',
      key: 'access_count',
    },
    {
      title: '过期时间',
      dataIndex: 'expires_at',
      key: 'expires_at',
      render: (date: string) => (date ? formatDate(date) : '永不过期'),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean, record: Share) => (
        <Switch
          checked={isActive}
          onChange={() => handleToggleActive(record.id, isActive)}
          checkedChildren="激活"
          unCheckedChildren="停用"
        />
      ),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Popconfirm
          title="确定删除此分享链接吗?"
          onConfirm={() => handleDelete(record.id)}
          okText="确定"
          cancelText="取消"
        >
          <Button type="link" danger icon={<DeleteOutlined />}>
            删除
          </Button>
        </Popconfirm>
      ),
    },
  ]

  return (
    <div>
      <Card
        title={
          <Space>
            <ShareAltOutlined />
            <Title level={4} style={{ margin: 0 }}>分享管理</Title>
          </Space>
        }
      >
        <Typography.Paragraph type="secondary">
          在对话页面可以创建分享链接。这里可以管理所有已创建的分享链接。
        </Typography.Paragraph>
        <Table
          columns={columns}
          dataSource={shares}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  )
}
