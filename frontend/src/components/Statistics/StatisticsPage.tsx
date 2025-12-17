import { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Select, Spin, message, Typography } from 'antd'
import {
  MessageOutlined,
  DollarOutlined,
  ApiOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons'
import { statisticsService } from '../../services'
import type { Statistics } from '../../types'
import { formatNumber, formatCost } from '../../utils/format'

const { Title } = Typography

export default function StatisticsPage() {
  const [statistics, setStatistics] = useState<Statistics | null>(null)
  const [loading, setLoading] = useState(false)
  const [days, setDays] = useState(30)

  useEffect(() => {
    fetchStatistics()
  }, [days])

  const fetchStatistics = async () => {
    setLoading(true)
    try {
      const data = await statisticsService.getUserStatistics(days)
      setStatistics(data)
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取统计数据失败')
    } finally {
      setLoading(false)
    }
  }

  if (loading || !statistics) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: 48 }}>
          <Spin size="large" />
        </div>
      </Card>
    )
  }

  return (
    <div>
      <Card
        title={<Title level={4} style={{ margin: 0 }}>使用统计</Title>}
        extra={
          <Select
            value={days}
            onChange={setDays}
            style={{ width: 150 }}
            options={[
              { value: 7, label: '最近 7 天' },
              { value: 30, label: '最近 30 天' },
              { value: 90, label: '最近 90 天' },
              { value: 365, label: '最近一年' },
            ]}
          />
        }
      >
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="总对话数"
                value={statistics.summary.total_conversations}
                prefix={<MessageOutlined />}
                valueStyle={{ color: '#3f8600' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="总消息数"
                value={formatNumber(statistics.summary.total_messages)}
                prefix={<MessageOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="总 Tokens"
                value={formatNumber(statistics.summary.total_tokens)}
                prefix={<ThunderboltOutlined />}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="总花费"
                value={formatCost(statistics.summary.total_cost)}
                prefix={<DollarOutlined />}
                valueStyle={{ color: '#cf1322' }}
              />
            </Card>
          </Col>
        </Row>

        {statistics.by_provider && Object.keys(statistics.by_provider).length > 0 && (
          <Card
            title="按提供商统计"
            style={{ marginTop: 16 }}
            bordered={false}
          >
            <Row gutter={[16, 16]}>
              {Object.entries(statistics.by_provider).map(([provider, data]) => (
                <Col xs={24} sm={12} lg={8} key={provider}>
                  <Card size="small">
                    <Statistic
                      title={provider.toUpperCase()}
                      value={formatCost(data.cost)}
                      prefix={<ApiOutlined />}
                      valueStyle={{ fontSize: 20 }}
                    />
                    <div style={{ marginTop: 8, fontSize: 12, color: '#8c8c8c' }}>
                      <div>对话: {data.conversations}</div>
                      <div>消息: {formatNumber(data.messages)}</div>
                      <div>Tokens: {formatNumber(data.tokens)}</div>
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        )}

        {statistics.by_model && Object.keys(statistics.by_model).length > 0 && (
          <Card
            title="按模型统计"
            style={{ marginTop: 16 }}
            bordered={false}
          >
            <Row gutter={[16, 16]}>
              {Object.entries(statistics.by_model).map(([model, data]) => (
                <Col xs={24} sm={12} lg={8} key={model}>
                  <Card size="small">
                    <Statistic
                      title={model}
                      value={formatCost(data.cost)}
                      valueStyle={{ fontSize: 16 }}
                    />
                    <div style={{ marginTop: 8, fontSize: 12, color: '#8c8c8c' }}>
                      <div>对话: {data.conversations}</div>
                      <div>消息: {formatNumber(data.messages)}</div>
                      <div>Tokens: {formatNumber(data.tokens)}</div>
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        )}
      </Card>
    </div>
  )
}
