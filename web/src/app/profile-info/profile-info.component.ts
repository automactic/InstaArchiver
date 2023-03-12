import { Component, Input } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';

import { Profile } from '../services/profile.service';
import { ListTasksResponse, TaskService } from '../services/task.service';


interface TreeNode<T> {
  data: T;
  children?: TreeNode<T>[];
  expanded?: boolean;
}

interface PostCount {
  year: string
  Q1: number
  Q2: number
  Q3: number
  Q4: number
}

@Component({
  selector: 'profile-info',
  templateUrl: './profile-info.component.html',
  styleUrls: ['./profile-info.component.scss']
})
export class ProfileInfoComponent {
  @Input() profile?: Profile
  allColumns = ['Year', 'Q4', 'Q3', 'Q2', 'Q1']
  postCounts: TreeNode<PostCount>[] = []
  taskService: TaskService

  tasks$: Observable<ListTasksResponse | null> = new BehaviorSubject(null)

  constructor(taskService: TaskService) {
    this.taskService = taskService
  }

  ngOnChanges(changes: any) {
    let profile = changes.profile.currentValue
    if (profile) {
      this.postCounts = Object.keys(profile.counts ?? {}).map(key => {
        let count = profile.counts[key] ?? {}
        return {
          data: {
            year: key,
            Q1: count['Q1'],
            Q2: count['Q2'],
            Q3: count['Q3'],
            Q4: count['Q4'],
          }
        }
      }).sort((lhs, rhs) => lhs.data.year < rhs.data.year ? 1 : -1)
      this.tasks$ = this.taskService.list(0, 5, profile.username)
    } else {
      this.postCounts = []
      this.tasks$ = new BehaviorSubject(null)
    }
  }
}
