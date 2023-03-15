import { Injectable } from '@angular/core'
import { HttpClient } from '@angular/common/http'

import { environment } from '../../environments/environment'

export interface Task {
  id: string
  username?: string
  type: string
  status: string
  created: Date
  started?: Date
  completed?: Date
  post_count?: number
}

export interface ListTasksResponse {
  tasks: Task[]
  limit: number
  offset: number
  count: number
}

@Injectable({providedIn: 'root'})
export class TaskService {
  constructor(private httpClient: HttpClient) { }

  list(offset: number = 0, limit: number = 10, username?: string) {
    let url = `${environment.apiRoot}/api/tasks/`
    let params: Record<string, string> = { offset: String(offset), limit: String(limit) }
    if (username) { 
      params['username'] = username 
    }
    return this.httpClient.get<ListTasksResponse>(url, {params: params})
  }
}