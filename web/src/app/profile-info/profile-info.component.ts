import { Component, Input, ViewChild, TemplateRef } from '@angular/core';
import { NbMenuService } from '@nebular/theme';
import { Observable, BehaviorSubject, filter, map, tap } from 'rxjs';

import { NbDialogService, NbDialogRef, NbCalendarRange } from '@nebular/theme';

import { ProfileWithDetails, ProfileService } from '../services/profile.service';
import { TaskService } from '../services/task.service';


interface PostStatNode<T> {
  data: T;
  children?: PostStatNode<T>[];
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
  profileService: ProfileService
  taskService: TaskService
  
  @Input() username?: string
  @ViewChild('timeRangeTaskCreationDialog') timeRangeTaskCreationDialog?: TemplateRef<any>
  allColumns = ['Year', 'Q4', 'Q3', 'Q2', 'Q1']
  taskActions = [{ title: 'Catch Up', icon: 'flash' }, { title: 'Time Range', icon: 'calendar' }];
  userDisplayName?: string
  timeRange: NbCalendarRange<Date> = { start: new Date() }
  stats: PostStatNode<PostCount>[] = []
  profile$: Observable<ProfileWithDetails | null> = new BehaviorSubject(null)

  constructor(
    private nbMenuService: NbMenuService, 
    private dialogService: NbDialogService,
    profileService: ProfileService, 
    taskService: TaskService
  ) {
    this.profileService = profileService
    this.taskService = taskService
    this.nbMenuService.onItemClick()
      .pipe(
        filter(menu => menu.tag === 'task-actions'),
        map(menu => menu.item.title),
      )
      .subscribe(title => this.handleTaskAction(title));
  }

  ngOnChanges(changes: any) {
    this.refresh()
  }

  private refresh() {
    if (this.username) {
      this.profile$ = this.profileService.get(this.username).pipe(
        tap(profile => {
          this.userDisplayName = profile.display_name
          this.stats = Object.keys(profile.stats.counts).map(key => {
            let count = profile.stats.counts[key] ?? {}
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
        })
      )
    } else {
      this.userDisplayName = undefined
      this.stats = []
      this.profile$ = new BehaviorSubject(null)
    }
  }

  showDialog(dialog: TemplateRef<any>): void {
    this.dialogService.open(dialog, { hasScroll: true })
  }

  handleTaskAction(title: String): void {
    if (title == 'Catch Up' && this.username) {
      this.taskService.createCatchUpTask([this.username]).subscribe(_ => {
        this.refresh()
      }) 
    } else if (title == 'Time Range' && this.timeRangeTaskCreationDialog) {
      let context = { userDisplayName: this.userDisplayName }
      this.dialogService.open(this.timeRangeTaskCreationDialog, { hasScroll: true, context: context })
    }
  }

  createTimeRangeTask(dialogRef: NbDialogRef<TemplateRef<any>>): void {
    if (this.username && this.timeRange.end) {
      this.taskService.createTimeRangeTask(this.username, this.timeRange.start, this.timeRange.end).subscribe(_ => {
        this.refresh()
        dialogRef.close()
      })
    }
  }

  changeDisplayName(dialogRef: NbDialogRef<TemplateRef<any>>): void {
    if (this.username && this.userDisplayName) {
      this.profileService.updateDisplayName(this.username, this.userDisplayName).subscribe(_ => {
        this.refresh()
        dialogRef.close()
      })
    }
  }

  copyUsername(): void {
    if (this.username) {
      navigator.clipboard.writeText(this.username)
    }
  }
}
